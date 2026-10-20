from unittest.mock import MagicMock, patch

import requests
from django.test import SimpleTestCase

from planner.geocode import geocode


def reply(data=None, error=None):
    response = MagicMock()
    response.json.return_value = data
    response.raise_for_status.side_effect = error
    return response


PHOTON_CHICAGO = {"features": [{"geometry": {"coordinates": [-87.62, 41.87]}}]}


@patch("planner.geocode.requests.get")
class GeocodeTests(SimpleTestCase):
    def test_uses_nominatim_first(self, get):
        get.return_value = reply([{"lat": "41.87", "lon": "-87.62"}])
        self.assertEqual(geocode("Chicago, IL"), (41.87, -87.62))
        self.assertEqual(get.call_count, 1)

    def test_falls_back_to_photon_when_blocked(self, get):
        get.side_effect = [reply(error=requests.HTTPError("403")), reply(PHOTON_CHICAGO)]
        self.assertEqual(geocode("Chicago, IL"), (41.87, -87.62))

    def test_falls_back_to_photon_on_html_reply(self, get):
        blocked = reply()
        blocked.json.side_effect = requests.JSONDecodeError("Expecting value", "\n<html>", 1)
        get.side_effect = [blocked, reply(PHOTON_CHICAGO)]
        self.assertEqual(geocode("Chicago, IL"), (41.87, -87.62))

    def test_unknown_place(self, get):
        get.return_value = reply([])
        with self.assertRaisesMessage(ValueError, "Could not find 'Nowhere'"):
            geocode("Nowhere")
