from unittest.mock import patch

from django.test import SimpleTestCase

from planner.routes import detour_point, parse_route, three_routes

OSRM_ROUTE = {
    "distance": 16093.44,
    "duration": 900,
    "geometry": {"coordinates": [[-90, 40], [-90.1, 40.05], [-90.2, 40.1]]},
    "legs": [{"annotation": {"distance": [8000, 8093.44], "duration": [450, 450]}}],
}


class ParseRouteTests(SimpleTestCase):
    def test_flips_coordinates_and_converts_units(self):
        route = parse_route(OSRM_ROUTE)
        self.assertEqual(route["coords"][0], [40, -90])
        self.assertEqual(route["miles"], 10)
        self.assertEqual(route["hours"], 0.25)
        self.assertEqual(len(route["distances"]), len(route["coords"]) - 1)


class DetourTests(SimpleTestCase):
    def test_point_is_beside_the_midpoint(self):
        self.assertEqual(detour_point((40, -90), (40, -80), 0.2), (38, -85))
        self.assertEqual(detour_point((40, -90), (40, -80), -0.2), (42, -85))


class ThreeRoutesTests(SimpleTestCase):
    @patch("planner.routes.fetch_routes")
    def test_adds_detours_until_three(self, fetch):
        fetch.side_effect = [[{"miles": 100}, {"miles": 110}], [{"miles": 100.5}], [{"miles": 125}]]
        self.assertEqual([r["miles"] for r in three_routes((40, -90), (41, -89))], [100, 110, 125])

    @patch("planner.routes.fetch_routes")
    def test_keeps_three_alternatives_without_detours(self, fetch):
        fetch.return_value = [{"miles": 1}, {"miles": 2}, {"miles": 3}, {"miles": 4}]
        self.assertEqual(len(three_routes((40, -90), (41, -89))), 3)
        fetch.assert_called_once()
