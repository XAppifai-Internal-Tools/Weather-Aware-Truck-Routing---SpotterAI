from datetime import timedelta

import requests

URL = "https://api.open-meteo.com/v1/forecast"
BATCH = 100


def to_hour(time):
    return (time + timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)


def hour_key(time):
    return to_hour(time).strftime("%Y-%m-%dT%H:00")


def fetch_forecast(points, start, end):
    """Hourly forecast for each (lat, lon) between start and end (UTC), as {hour: (wind, rain, snow)}."""
    forecasts = []
    for i in range(0, len(points), BATCH):
        batch = points[i:i + BATCH]
        params = {
            "latitude": ",".join(f"{lat:.3f}" for lat, _ in batch),
            "longitude": ",".join(f"{lon:.3f}" for _, lon in batch),
            "hourly": "wind_speed_10m,rain,snowfall",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "GMT",
            "start_hour": hour_key(start),
            "end_hour": hour_key(end),
        }
        data = requests.get(URL, params=params, timeout=30).json()
        if isinstance(data, dict) and data.get("error"):
            raise ValueError(f"Weather forecast unavailable: {data.get('reason')}")
        for place in data if isinstance(data, list) else [data]:
            hourly = place["hourly"]
            values = zip(hourly["wind_speed_10m"], hourly["rain"], hourly["snowfall"])
            forecasts.append(dict(zip(hourly["time"], values)))
    return forecasts
