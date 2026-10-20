import requests

NOMINATIM = "https://nominatim.openstreetmap.org/search"
PHOTON = "https://photon.komoot.io/api/"
HEADERS = {"User-Agent": "weather-aware-truck-routing"}


def nominatim(place):
    response = requests.get(NOMINATIM, params={"q": place, "format": "json", "limit": 1}, headers=HEADERS, timeout=15)
    response.raise_for_status()
    found = response.json()
    return (float(found[0]["lat"]), float(found[0]["lon"])) if found else None


def photon(place):
    response = requests.get(PHOTON, params={"q": place, "limit": 1}, headers=HEADERS, timeout=15)
    response.raise_for_status()
    found = response.json()["features"]
    return (found[0]["geometry"]["coordinates"][1], found[0]["geometry"]["coordinates"][0]) if found else None


def geocode(place):
    # Nominatim often blocks shared cloud servers, so Photon is the backup
    try:
        point = nominatim(place)
    except (requests.RequestException, ValueError):
        point = photon(place)
    if not point:
        raise ValueError(f"Could not find '{place}'")
    return point
