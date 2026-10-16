from datetime import timedelta

from .routes import METERS_PER_MILE


def make_checkpoints(route, departure, every_miles):
    """Points every `every_miles` along the route (plus start and end) with the truck's ETA."""
    coords = route["coords"]
    points = []
    miles = seconds = 0.0
    next_mile = every_miles

    def add(i):
        lat, lon = coords[i]
        points.append({"lat": lat, "lon": lon, "mile": round(miles, 1), "eta": departure + timedelta(seconds=round(seconds))})

    add(0)
    for i, (meters, secs) in enumerate(zip(route["distances"], route["durations"]), start=1):
        miles += meters / METERS_PER_MILE
        seconds += secs
        if miles >= next_mile:
            add(i)
            while next_mile <= miles:
                next_mile += every_miles
    if points[-1]["mile"] < round(miles, 1):
        add(len(coords) - 1)

    # each checkpoint stands for the road halfway to its neighbours
    for i, point in enumerate(points):
        before = points[i - 1]["mile"] if i > 0 else point["mile"]
        after = points[i + 1]["mile"] if i < len(points) - 1 else point["mile"]
        point["miles"] = round((after - before) / 2, 2)
    return points
