from .risk import HIGH, NO_TRAVEL, SEVERE


def summarize(checkpoints):
    total = sum(c["miles"] for c in checkpoints) or 1

    def miles_at(level):
        return round(sum(c["miles"] for c in checkpoints if c["risk"] == level), 1)

    return {
        "no_travel_miles": miles_at(NO_TRAVEL),
        "severe_miles": miles_at(SEVERE),
        "high_miles": miles_at(HIGH),
        "avg_risk": round(sum(c["risk"] * c["miles"] for c in checkpoints) / total, 2),
        "worst_risk": max(c["risk"] for c in checkpoints),
    }


def best_route(routes):
    """Index of the route with the fewest severe miles, then high miles, average risk and travel time."""
    return min(
        range(len(routes)),
        key=lambda i: (
            routes[i]["no_travel_miles"],
            routes[i]["severe_miles"],
            routes[i]["high_miles"],
            routes[i]["avg_risk"],
            routes[i]["hours"],
        ),
    )
