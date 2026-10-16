import requests

URL = "https://nominatim.openstreetmap.org/search"


def geocode(place):
    params = {"q": place, "format": "json", "limit": 1}
    headers = {"User-Agent": "weather-aware-truck-routing"}
    found = requests.get(URL, params=params, headers=headers, timeout=15).json()
    if not found:
        raise ValueError(f"Could not find '{place}'")
    return float(found[0]["lat"]), float(found[0]["lon"])
