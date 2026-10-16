# Weather-Aware Truck Routing

Helps a truck driver pick the safest route based on weather along the way, load weight and travel time.

- **Frontend:** Next.js (React) + Leaflet, in `app/`
- **Backend:** Django, in `backend/`
- **Free APIs, no keys needed:** OSRM (routes), Nominatim (geocoding), Open-Meteo (hourly forecast)

## Run it

Backend (Python 3.10 or newer; on macOS the built-in Python 3.9 is too old, `uv venv --python 3.12 .venv` works):

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py runserver 8000
```

Frontend (in another terminal):

```bash
npm install
npm run dev
```

Open http://localhost:3000. Next.js forwards `/api/*` to Django on port 8000.

## Tests

```bash
cd backend && .venv/bin/python manage.py test
```

## How it works

1. Origin and destination are geocoded, and OSRM returns up to 3 routes. If it gives fewer, a detour
   point beside the direct line is added to get another real alternative.
2. Checkpoints are placed every 10, 25 or 50 miles (your choice), plus the start and the end. Each
   checkpoint's ETA comes from OSRM's drive time for each road segment, counted from the departure time.
3. The hourly forecast at each checkpoint's ETA (rounded to the nearest hour) gives wind (mph), rain and
   snow (in/hr). Each is rated with the risk table, then the load rules are applied to wind:

   | Condition | Low | Moderate | High | Severe | No Travel |
   |-----------|-----|----------|------|--------|-----------|
   | Wind | <25 mph | 25–34 | 35–44 | 45–54 | ≥55 mph |
   | Rain | <0.10 in/hr | 0.10–0.25 | 0.25–0.50 | 0.50–1.00 | >1.00 |
   | Snow | <0.5 in/hr | 0.5–1.0 | 1.0–2.0 | 2.0–3.0 | >3.0 |

   - 45–54 mph with a load over 30,000 lb is No Travel
   - 35–44 mph with a load over 40,000 lb is Severe

   A checkpoint's risk is the worst of the three. Each checkpoint covers the road halfway to its
   neighbours, so the route's "severe miles", "high miles" and average risk are weighted by distance.
4. The recommended route has the fewest No Travel miles, then the fewest Severe miles, then the fewest
   High miles, then the lowest average risk, then the shortest travel time.
5. The heatmap is a grid of cells along the trip corridor, rated with the same rules for every hour from
   departure to 48 hours after. The slider picks the hour.

## Project layout

```
app/
  page.tsx                  page layout and state
  components/TripForm.tsx   origin, destination, departure, load, interval
  components/RouteList.tsx  route summaries and the checkpoint table
  components/RouteMap.tsx   routes, checkpoints and heatmap on the map
  components/ForecastSlider.tsx  0–48 h heatmap slider and legend
  format.ts                 risk colours, labels, time formatting
  types.ts                  shapes returned by the API

backend/planner/
  views.py        POST /api/plan, puts everything together
  geocode.py      place name to coordinates
  routes.py       3 route options from OSRM
  checkpoints.py  checkpoints and ETAs along a route
  weather.py      hourly forecast from Open-Meteo
  risk.py         risk table and load rules
  ranking.py      route totals and the recommendation
  heatmap.py      grid cells along the corridor
  tests/          one test file per module
```

## Notes

- Drive times come from OSRM's car profile, so real truck times can be a little longer.
- Open-Meteo forecasts cover about 16 days, so the trip has to fit inside that window.
- Open-Meteo's free tier has a per-minute limit. Planning many long trips back to back may need a short wait.
