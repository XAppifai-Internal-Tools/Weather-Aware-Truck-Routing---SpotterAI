import { formatHours, formatTime, RISK_COLORS, RISK_LABELS, ROUTE_COLORS } from "../format";
import type { Plan } from "../types";

type Props = { plan: Plan; selected: number; onSelect: (index: number) => void };

export default function RouteList({ plan, selected, onSelect }: Props) {
  const route = plan.routes[selected];

  return (
    <div className="space-y-3">
      {plan.routes.map((r, i) => (
        <button
          key={r.name}
          onClick={() => onSelect(i)}
          className={`w-full rounded border p-3 text-left text-sm ${i === selected ? "border-zinc-900 bg-zinc-50" : "border-zinc-200"}`}
        >
          <div className="flex items-center justify-between font-medium">
            <span>
              <span className="mr-2 inline-block h-2 w-4 rounded" style={{ background: ROUTE_COLORS[i] }} />
              {r.name}
            </span>
            {i === plan.best && <span className="rounded bg-green-600 px-2 py-0.5 text-xs text-white">Recommended</span>}
          </div>
          <div className="mt-1 text-zinc-600">
            {r.miles} mi · {formatHours(r.hours)} · worst{" "}
            <span style={{ color: RISK_COLORS[r.worst_risk] }}>{RISK_LABELS[r.worst_risk]}</span>
          </div>
          <div className="text-xs text-zinc-500">
            No travel {r.no_travel_miles} mi · Severe {r.severe_miles} mi · High {r.high_miles} mi · Avg risk {r.avg_risk}
          </div>
        </button>
      ))}

      <p className="text-xs text-zinc-500">
        Recommended by fewest severe miles, then high miles, then lowest average risk, then shortest time.
      </p>

      <table className="w-full text-xs">
        <thead className="text-left text-zinc-500">
          <tr><th>Mile</th><th>ETA</th><th>Wind mph</th><th>Rain in/hr</th><th>Snow in/hr</th><th>Risk</th></tr>
        </thead>
        <tbody>
          {route.checkpoints.map((c) => (
            <tr key={c.mile} className="border-t border-zinc-100">
              <td>{c.mile}</td>
              <td>{formatTime(c.eta)}</td>
              <td>{c.wind}</td>
              <td>{c.rain}</td>
              <td>{c.snow}</td>
              <td style={{ color: RISK_COLORS[c.risk] }}>{RISK_LABELS[c.risk]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
