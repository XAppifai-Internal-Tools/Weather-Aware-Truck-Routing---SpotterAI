import math

from django.test import SimpleTestCase

from planner.heatmap import CELLS_ACROSS, corridor_cells


class CorridorTests(SimpleTestCase):
    def test_cells_cover_every_route_point(self):
        routes = [{"coords": [[40 + i * 0.1, -90 + i * 0.05] for i in range(30)]},
                  {"coords": [[40 + i * 0.1, -90 - i * 0.02] for i in range(30)]}]
        size, cells = corridor_cells(routes)
        self.assertAlmostEqual(size, 2.9 / CELLS_ACROSS)
        for route in routes:
            for lat, lon in route["coords"]:
                nearest = min(math.hypot(lat - c[0], lon - c[1]) for c in cells)
                self.assertLessEqual(nearest, size)

    def test_corridor_is_not_the_whole_box(self):
        size, cells = corridor_cells([{"coords": [[40 + i * 0.1, -90 + i * 0.1] for i in range(40)]}])
        self.assertLess(len(cells), (CELLS_ACROSS + 2) ** 2 / 2)

    def test_short_trip_has_minimum_cell_size(self):
        size, cells = corridor_cells([{"coords": [[40, -90], [40.01, -90.01]]}])
        self.assertEqual(size, 0.05)
        self.assertEqual(len(cells), 9)
