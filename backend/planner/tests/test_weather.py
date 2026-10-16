from datetime import datetime, timezone
from unittest.mock import patch

from django.test import SimpleTestCase

from planner.weather import fetch_forecast, hour_key

START = datetime(2026, 10, 17, 8, 10, tzinfo=timezone.utc)


def place(wind):
    return {"hourly": {"time": ["2026-10-17T08:00", "2026-10-17T09:00"], "wind_speed_10m": [wind, None],
                       "rain": [0.1, None], "snowfall": [0.0, None]}}


class HourTests(SimpleTestCase):
    def test_rounds_to_nearest_hour(self):
        self.assertEqual(hour_key(START), "2026-10-17T08:00")
        self.assertEqual(hour_key(START.replace(minute=30)), "2026-10-17T09:00")
        self.assertEqual(hour_key(START.replace(hour=23, minute=45)), "2026-10-18T00:00")


class FetchForecastTests(SimpleTestCase):
    @patch("planner.weather.requests.get")
    def test_reads_each_place_in_batches(self, get):
        get.return_value.json.side_effect = [[place(i) for i in range(100)], place(7)]
        forecasts = fetch_forecast([(40, -90)] * 101, START, START)
        self.assertEqual(get.call_count, 2)
        self.assertEqual(len(forecasts), 101)
        self.assertEqual(forecasts[100]["2026-10-17T08:00"], (7, 0.1, 0.0))
        params = get.call_args.kwargs["params"]
        self.assertEqual(params["wind_speed_unit"], "mph")
        self.assertEqual(params["precipitation_unit"], "inch")

    @patch("planner.weather.requests.get")
    def test_api_error_becomes_value_error(self, get):
        get.return_value.json.return_value = {"error": True, "reason": "out of range"}
        with self.assertRaisesMessage(ValueError, "out of range"):
            fetch_forecast([(40, -90)], START, START)
