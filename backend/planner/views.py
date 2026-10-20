import json
from datetime import datetime, timedelta, timezone

import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .checkpoints import make_checkpoints
from .geocode import geocode
from .heatmap import corridor_cells
from .ranking import best_route, summarize
from .risk import weather_risk
from .routes import three_routes
from .weather import fetch_forecast, hour_key, to_hour

INTERVALS = (10, 25, 50)
HEATMAP_HOURS = 48


def read_trip(body):
    trip = json.loads(body)
    departure = datetime.fromisoformat(trip["departure"].replace("Z", "+00:00"))
    if departure.tzinfo is None:
        raise ValueError("Departure must include a time zone")
    weight = float(trip["weight"])
    interval = int(trip["interval"])
    if weight <= 0:
        raise ValueError("Load weight must be positive")
    if interval not in INTERVALS:
        raise ValueError("Interval must be 10, 25 or 50 miles")
    return trip["origin"], trip["destination"], departure.astimezone(timezone.utc), weight, interval


def risk_at(forecast, time, weight):
    values = forecast.get(hour_key(time))
    if values is None or None in values:
        return None
    return weather_risk(*values, weight)


def plan_routes(origin, destination, departure, weight, interval):
    routes = three_routes(geocode(origin), geocode(destination))
    stops = [make_checkpoints(route, departure, interval) for route in routes]
    flat = [stop for route_stops in stops for stop in route_stops]
    forecasts = fetch_forecast([(s["lat"], s["lon"]) for s in flat], departure, max(s["eta"] for s in flat))

    for stop, forecast in zip(flat, forecasts):
        stop["risk"] = risk_at(forecast, stop["eta"], weight)
        if stop["risk"] is None:
            raise ValueError("Trip goes beyond the available weather forecast")
        stop["wind"], stop["rain"], stop["snow"] = forecast[hour_key(stop["eta"])]
        stop["eta"] = stop["eta"].isoformat()

    result = []
    for name, route, route_stops in zip("ABC", routes, stops):
        result.append({"name": f"Route {name}", "coords": route["coords"], "miles": route["miles"],
                       "hours": route["hours"], "checkpoints": route_stops, **summarize(route_stops)})
    return result


def plan_heatmap(routes, departure, weight):
    size, cells = corridor_cells(routes)
    start = to_hour(departure)
    forecasts = fetch_forecast(cells, start, start + timedelta(hours=HEATMAP_HOURS))
    hours = [start + timedelta(hours=h) for h in range(HEATMAP_HOURS + 1)]
    return {
        "start": start.isoformat(),
        "size": size,
        "cells": [{"lat": lat, "lon": lon, "risk": [risk_at(forecast, h, weight) for h in hours]}
                  for (lat, lon), forecast in zip(cells, forecasts)],
    }


@require_POST
def plan(request):
    try:
        origin, destination, departure, weight, interval = read_trip(request.body)
        routes = plan_routes(origin, destination, departure, weight, interval)
        heatmap = plan_heatmap(routes, departure, weight)
    except KeyError as error:
        return JsonResponse({"error": f"Missing {error.args[0]}"}, status=400)
    except (TypeError, ValueError) as error:
        return JsonResponse({"error": str(error) or "Invalid trip details"}, status=400)
    except requests.RequestException:
        return JsonResponse({"error": "A map or weather service did not respond, try again"}, status=502)
    return JsonResponse({"routes": routes, "best": best_route(routes), "heatmap": heatmap})
