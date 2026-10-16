import math

CELLS_ACROSS = 12


def corridor_cells(routes):
    """Grid cells covering every route plus one cell on each side."""
    points = [p for route in routes for p in route["coords"]]
    lat0 = min(p[0] for p in points)
    lon0 = min(p[1] for p in points)
    span = max(max(p[0] for p in points) - lat0, max(p[1] for p in points) - lon0)
    size = max(span / CELLS_ACROSS, 0.05)
    hit = {(math.floor((lat - lat0) / size), math.floor((lon - lon0) / size)) for lat, lon in points}
    cells = {(i + di, j + dj) for i, j in hit for di in (-1, 0, 1) for dj in (-1, 0, 1)}
    return size, [(round(lat0 + (i + 0.5) * size, 4), round(lon0 + (j + 0.5) * size, 4)) for i, j in sorted(cells)]
