import json
from unittest.mock import patch

import requests
from django.test import SimpleTestCase

from planner.routes import METERS_PER_MILE

TRIP = {"origin": "Chicago, IL", "destination": "St. Louis, MO", "departure": "2026-10-17T08:00:00.000Z",
        "weight": 42000, "interval": 25}


def route(miles, hours):
    return {"coords": [[40.0, -90 + i * 0.01] for i in range(miles + 1)], "distances": [METERS_PER_MILE] * miles,
            "durations": [hours * 3600 / miles] * miles, "miles": miles, "hours": hours}


def fake_forecast(windy_lon):
    """Calm everywhere except 40 mph wind east of `windy_lon`, for 3 days from departure."""
    def fetch(points, start, end):
        hours = [f"2026-10-{day}T{h:02d}:00" for day in (17, 18, 19) for h in range(24)]
        return [{t: (40 if lon > windy_lon else 5, 0.0, 0.0) for t in hours} for _, lon in points]
    return fetch


@patch("planner.views.geocode", return_value=(40, -90))
class PlanViewTests(SimpleTestCase):
    def post(self, trip):
        return self.client.post("/api/plan", json.dumps(trip), content_type="application/json")

    @patch("planner.views.fetch_forecast", side_effect=fake_forecast(-89.5))
    @patch("planner.views.three_routes", return_value=[route(100, 2), route(40, 1), route(120, 3)])
    def test_avoids_severe_wind_for_heavy_load(self, routes, forecast, geocode):
        data = self.post(TRIP).json()
        a, b, c = data["routes"]
        self.assertEqual([r["name"] for r in data["routes"]], ["Route A", "Route B", "Route C"])
        self.assertEqual(a["severe_miles"], 37.5)
        self.assertEqual(c["severe_miles"], 57.5)
        self.assertEqual(b["severe_miles"], 0)
        self.assertEqual(data["best"], 1)
        self.assertEqual([p["mile"] for p in a["checkpoints"]], [0, 25, 50, 75, 100])
        self.assertEqual(a["checkpoints"][2]["eta"], "2026-10-17T09:00:00+00:00")
        self.assertEqual(a["checkpoints"][4]["wind"], 40)

    @patch("planner.views.fetch_forecast", side_effect=fake_forecast(-89.5))
    @patch("planner.views.three_routes", return_value=[route(100, 2), route(40, 1)])
    def test_light_load_is_only_high_risk(self, routes, forecast, geocode):
        data = self.post({**TRIP, "weight": 20000}).json()
        self.assertEqual(data["routes"][0]["severe_miles"], 0)
        self.assertEqual(data["routes"][0]["high_miles"], 37.5)

    @patch("planner.views.fetch_forecast", side_effect=fake_forecast(-89.5))
    @patch("planner.views.three_routes", return_value=[route(100, 2)])
    def test_heatmap_has_49_hours_per_cell(self, routes, forecast, geocode):
        heatmap = self.post(TRIP).json()["heatmap"]
        self.assertEqual(heatmap["start"], "2026-10-17T08:00:00+00:00")
        self.assertTrue(heatmap["cells"])
        for cell in heatmap["cells"]:
            self.assertEqual(len(cell["risk"]), 49)
        windy = [c for c in heatmap["cells"] if c["lon"] > -89.5]
        self.assertTrue(windy and all(set(c["risk"]) == {3} for c in windy))

    @patch("planner.views.fetch_forecast", return_value=[{}] * 50)
    @patch("planner.views.three_routes", return_value=[route(100, 2)])
    def test_trip_beyond_forecast(self, routes, forecast, geocode):
        response = self.post(TRIP)
        self.assertEqual(response.status_code, 400)
        self.assertIn("beyond the available weather forecast", response.json()["error"])

    def test_rejects_bad_input(self, geocode):
        for bad in [{**TRIP, "interval": 30}, {**TRIP, "weight": -1}, {**TRIP, "departure": "2026-10-17T08:00"},
                    {**TRIP, "departure": "tomorrow"}, {k: v for k, v in TRIP.items() if k != "origin"}]:
            response = self.post(bad)
            self.assertEqual(response.status_code, 400, bad)
            self.assertTrue(response.json()["error"])

    def test_only_post_is_allowed(self, geocode):
        self.assertEqual(self.client.get("/api/plan").status_code, 405)

    @patch("planner.views.three_routes", side_effect=requests.ConnectionError)
    def test_service_down(self, routes, geocode):
        self.assertEqual(self.post(TRIP).status_code, 502)
