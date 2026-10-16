"use client";

import "leaflet/dist/leaflet.css";
import { useEffect } from "react";
import { CircleMarker, MapContainer, Pane, Polyline, Rectangle, TileLayer, Tooltip, useMap } from "react-leaflet";
import { formatHours, formatTime, RISK_COLORS, RISK_LABELS, ROUTE_COLORS } from "../format";
import type { Plan } from "../types";

type Props = { plan: Plan | null; selected: number; hour: number; onSelect: (index: number) => void };

function FitRoutes({ plan }: { plan: Plan }) {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(plan.routes.flatMap((r) => r.coords), { padding: [40, 40] });
  }, [map, plan]);
  return null;
}

export default function RouteMap({ plan, selected, hour, onSelect }: Props) {
  const half = (plan?.heatmap.size ?? 0) / 2;

  return (
    <MapContainer center={[39.5, -98.35]} zoom={4} className="h-full w-full">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Pane name="heatmap" style={{ zIndex: 350 }} />
      <Pane name="selected" style={{ zIndex: 420 }} />
      <Pane name="checkpoints" style={{ zIndex: 450 }} />

      {plan && <FitRoutes plan={plan} />}

      {plan?.heatmap.cells.map((cell) => {
        const risk = cell.risk[hour];
        if (risk == null) return null;
        return (
          <Rectangle
            key={`${cell.lat},${cell.lon}`}
            pane="heatmap"
            bounds={[[cell.lat - half, cell.lon - half], [cell.lat + half, cell.lon + half]]}
            pathOptions={{ stroke: false, fillColor: RISK_COLORS[risk], fillOpacity: 0.35 }}
          />
        );
      })}

      {plan?.routes.map((route, i) => (
        <Polyline
          key={`${route.name}-${i === selected}`}
          pane={i === selected ? "selected" : "overlayPane"}
          positions={route.coords}
          pathOptions={{ color: ROUTE_COLORS[i], weight: i === selected ? 7 : 4, opacity: i === selected ? 0.9 : 0.5 }}
          eventHandlers={{ click: () => onSelect(i) }}
        >
          <Tooltip sticky>
            <b>{route.name}{i === plan.best && " (Recommended)"}</b>
            <br />
            {route.miles} mi · {formatHours(route.hours)}
            <br />
            Severe {route.severe_miles} mi · High {route.high_miles} mi · Avg risk {route.avg_risk}
          </Tooltip>
        </Polyline>
      ))}

      {plan?.routes.map((route, i) =>
        route.checkpoints.map((c) => (
          <CircleMarker
            key={`${route.name}-${c.mile}`}
            pane="checkpoints"
            center={[c.lat, c.lon]}
            radius={i === selected ? 7 : 4}
            pathOptions={{ color: "white", weight: 1.5, fillColor: RISK_COLORS[c.risk], fillOpacity: 1 }}
            eventHandlers={{ click: () => onSelect(i) }}
          >
            <Tooltip>
              <b>{route.name} · mile {c.mile}</b>
              <br />
              ETA {formatTime(c.eta)}
              <br />
              Wind {c.wind} mph · Rain {c.rain} in/hr · Snow {c.snow} in/hr
              <br />
              Risk: <b style={{ color: RISK_COLORS[c.risk] }}>{RISK_LABELS[c.risk]}</b>
            </Tooltip>
          </CircleMarker>
        )),
      )}
    </MapContainer>
  );
}
