from django.test import SimpleTestCase

from planner.ranking import best_route, summarize
from planner.risk import HIGH, LOW, MODERATE, NO_TRAVEL, SEVERE


def stops(*pairs):
    return [{"risk": risk, "miles": miles} for risk, miles in pairs]


def route(hours=5, no_travel=0, severe=0, high=0, avg=0):
    return {"hours": hours, "no_travel_miles": no_travel, "severe_miles": severe, "high_miles": high, "avg_risk": avg}


class SummarizeTests(SimpleTestCase):
    def test_counts_miles_by_level(self):
        summary = summarize(stops((LOW, 10), (HIGH, 20), (SEVERE, 5), (NO_TRAVEL, 5), (MODERATE, 10)))
        self.assertEqual(summary["high_miles"], 20)
        self.assertEqual(summary["severe_miles"], 5)
        self.assertEqual(summary["no_travel_miles"], 5)
        self.assertEqual(summary["worst_risk"], NO_TRAVEL)

    def test_average_risk_is_weighted_by_miles(self):
        self.assertEqual(summarize(stops((LOW, 30), (HIGH, 10)))["avg_risk"], 0.5)


class BestRouteTests(SimpleTestCase):
    def test_fewest_severe_miles_first(self):
        self.assertEqual(best_route([route(hours=4, severe=10), route(hours=6, high=50, avg=2)]), 1)

    def test_no_travel_is_avoided_before_anything(self):
        self.assertEqual(best_route([route(no_travel=5), route(severe=40, hours=9)]), 1)

    def test_then_fewest_high_miles(self):
        self.assertEqual(best_route([route(hours=4, high=20), route(hours=6, high=10)]), 1)

    def test_then_lowest_average_risk(self):
        self.assertEqual(best_route([route(hours=4, avg=0.8), route(hours=6, avg=0.3)]), 1)

    def test_then_shortest_time(self):
        self.assertEqual(best_route([route(hours=6), route(hours=4), route(hours=5)]), 1)
