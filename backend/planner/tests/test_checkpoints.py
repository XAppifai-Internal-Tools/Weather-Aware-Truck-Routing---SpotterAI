from datetime import datetime, timedelta, timezone

from django.test import SimpleTestCase

from planner.checkpoints import make_checkpoints
from planner.routes import METERS_PER_MILE

DEPARTURE = datetime(2026, 10, 17, 8, tzinfo=timezone.utc)


def straight_route(miles):
    """One coordinate per mile, driven at 60 mph."""
    return {
        "coords": [[40.0, -100.0 + i * 0.01] for i in range(miles + 1)],
        "distances": [METERS_PER_MILE] * miles,
        "durations": [60] * miles,
    }


class CheckpointTests(SimpleTestCase):
    def test_every_10_miles(self):
        points = make_checkpoints(straight_route(100), DEPARTURE, 10)
        self.assertEqual([p["mile"] for p in points], list(range(0, 101, 10)))

    def test_every_25_and_50_miles_include_destination(self):
        self.assertEqual([p["mile"] for p in make_checkpoints(straight_route(105), DEPARTURE, 25)], [0, 25, 50, 75, 100, 105])
        self.assertEqual([p["mile"] for p in make_checkpoints(straight_route(105), DEPARTURE, 50)], [0, 50, 100, 105])

    def test_eta_follows_drive_time(self):
        points = make_checkpoints(straight_route(100), DEPARTURE, 25)
        self.assertEqual(points[0]["eta"], DEPARTURE)
        self.assertEqual(points[2]["eta"], DEPARTURE + timedelta(minutes=50))
        self.assertEqual(points[-1]["eta"], DEPARTURE + timedelta(minutes=100))
        self.assertEqual(points[2]["lon"], -99.5)

    def test_checkpoint_miles_add_up_to_route_length(self):
        points = make_checkpoints(straight_route(105), DEPARTURE, 25)
        self.assertAlmostEqual(sum(p["miles"] for p in points), 105)
        self.assertEqual([p["miles"] for p in points], [12.5, 25, 25, 25, 15, 2.5])

    def test_long_segment_gives_one_checkpoint(self):
        route = {"coords": [[0, 0], [0, 1], [0, 2]], "distances": [35 * METERS_PER_MILE, 5 * METERS_PER_MILE], "durations": [1800, 300]}
        self.assertEqual([p["mile"] for p in make_checkpoints(route, DEPARTURE, 10)], [0, 35, 40])
