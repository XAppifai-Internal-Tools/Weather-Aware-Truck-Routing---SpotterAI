from django.test import SimpleTestCase

from planner.risk import HIGH, LOW, MODERATE, NO_TRAVEL, SEVERE, rain_risk, snow_risk, weather_risk, wind_risk

LIGHT = 20000


class WindRiskTests(SimpleTestCase):
    def test_thresholds(self):
        cases = [(0, LOW), (24.9, LOW), (25, MODERATE), (34.9, MODERATE), (35, HIGH), (44.9, HIGH),
                 (45, SEVERE), (54.9, SEVERE), (55, NO_TRAVEL), (80, NO_TRAVEL)]
        for mph, level in cases:
            self.assertEqual(wind_risk(mph, LIGHT), level, mph)

    def test_55_mph_stops_any_load(self):
        self.assertEqual(wind_risk(55, 1000), NO_TRAVEL)

    def test_45_to_54_mph_stops_loads_over_30000(self):
        self.assertEqual(wind_risk(45, 30000), SEVERE)
        self.assertEqual(wind_risk(45, 30001), NO_TRAVEL)
        self.assertEqual(wind_risk(54.9, 45000), NO_TRAVEL)

    def test_35_to_44_mph_is_severe_for_loads_over_40000(self):
        self.assertEqual(wind_risk(35, 40000), HIGH)
        self.assertEqual(wind_risk(35, 40001), SEVERE)
        self.assertEqual(wind_risk(44.9, 50000), SEVERE)
        self.assertEqual(wind_risk(34.9, 50000), MODERATE)


class RainRiskTests(SimpleTestCase):
    def test_thresholds(self):
        cases = [(0, LOW), (0.09, LOW), (0.1, MODERATE), (0.24, MODERATE), (0.25, HIGH), (0.49, HIGH),
                 (0.5, SEVERE), (1.0, SEVERE), (1.01, NO_TRAVEL)]
        for inches, level in cases:
            self.assertEqual(rain_risk(inches), level, inches)


class SnowRiskTests(SimpleTestCase):
    def test_thresholds(self):
        cases = [(0, LOW), (0.49, LOW), (0.5, MODERATE), (0.99, MODERATE), (1.0, HIGH), (1.99, HIGH),
                 (2.0, SEVERE), (3.0, SEVERE), (3.01, NO_TRAVEL)]
        for inches, level in cases:
            self.assertEqual(snow_risk(inches), level, inches)


class WeatherRiskTests(SimpleTestCase):
    def test_worst_condition_wins(self):
        self.assertEqual(weather_risk(10, 0, 0, LIGHT), LOW)
        self.assertEqual(weather_risk(30, 0.3, 0, LIGHT), HIGH)
        self.assertEqual(weather_risk(10, 0, 2.5, LIGHT), SEVERE)
        self.assertEqual(weather_risk(40, 0.1, 0.6, 45000), SEVERE)
        self.assertEqual(weather_risk(50, 0, 0, 35000), NO_TRAVEL)
