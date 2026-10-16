import requests

URL = "https://router.project-osrm.org/route/v1/driving/"
METERS_PER_MILE = 1609.344


def fetch_routes(points, alternatives=False):
    coords = ";".join(f"{lon},{lat}" for lat, lon in points)
    params = {
        "overview": "full",
        "geometries": "geojson",
        "annotations": "distance,duration",
        "alternatives": "3" if alternatives else "false",
    }
    data = requests.get(URL + coords, params=params, timeout=30).json()
    if data.get("code") != "Ok":
        raise ValueError("No driving route found between these places")
    return [parse_route(route) for route in data["routes"]]


def parse_route(route):
    distances, durations = [], []
    for leg in route["legs"]:
        distances += leg["annotation"]["distance"]
        durations += leg["annotation"]["duration"]
    return {
        "coords": [[lat, lon] for lon, lat in route["geometry"]["coordinates"]],
        "distances": distances,
        "durations": durations,
        "miles": round(route["distance"] / METERS_PER_MILE, 1),
        "hours": round(route["duration"] / 3600, 2),
    }


def detour_point(start, end, offset):
    """A point beside the straight line between start and end, used to force a different route."""
    mid_lat, mid_lon = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
    return mid_lat - (end[1] - start[1]) * offset, mid_lon + (end[0] - start[0]) * offset


def three_routes(start, end):
    routes = fetch_routes([start, end], alternatives=True)
    for offset in (0.15, -0.15, 0.3, -0.3):
        if len(routes) >= 3:
            break
        try:
            route = fetch_routes([start, detour_point(start, end, offset), end])[0]
        except ValueError:
            continue
        if all(abs(route["miles"] - other["miles"]) > 1 for other in routes):
            routes.append(route)
    return routes[:3]
