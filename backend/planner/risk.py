LEVELS = ["Low", "Moderate", "High", "Severe", "No Travel"]
LOW, MODERATE, HIGH, SEVERE, NO_TRAVEL = range(5)


def wind_risk(mph, load_lb):
    if mph >= 55:
        return NO_TRAVEL
    if mph >= 45:
        return NO_TRAVEL if load_lb > 30000 else SEVERE
    if mph >= 35:
        return SEVERE if load_lb > 40000 else HIGH
    return MODERATE if mph >= 25 else LOW


def rain_risk(inches_per_hour):
    if inches_per_hour > 1.0:
        return NO_TRAVEL
    if inches_per_hour >= 0.5:
        return SEVERE
    if inches_per_hour >= 0.25:
        return HIGH
    return MODERATE if inches_per_hour >= 0.1 else LOW


def snow_risk(inches_per_hour):
    if inches_per_hour > 3.0:
        return NO_TRAVEL
    if inches_per_hour >= 2.0:
        return SEVERE
    if inches_per_hour >= 1.0:
        return HIGH
    return MODERATE if inches_per_hour >= 0.5 else LOW


def weather_risk(wind_mph, rain_in, snow_in, load_lb):
    return max(wind_risk(wind_mph, load_lb), rain_risk(rain_in), snow_risk(snow_in))
