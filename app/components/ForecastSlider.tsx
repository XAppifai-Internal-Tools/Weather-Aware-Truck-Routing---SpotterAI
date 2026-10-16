import { formatTime, RISK_COLORS, RISK_LABELS } from "../format";

type Props = { start: string; hour: number; onChange: (hour: number) => void };

export default function ForecastSlider({ start, hour, onChange }: Props) {
  const time = new Date(new Date(start).getTime() + hour * 3600 * 1000).toISOString();

  return (
    <div className="rounded bg-white/95 p-3 text-sm shadow">
      <div className="flex justify-between">
        <span>Weather heatmap: departure +{hour}h</span>
        <span className="text-zinc-500">{formatTime(time)}</span>
      </div>
      <input
        type="range"
        min={0}
        max={48}
        value={hour}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
        aria-label="Forecast hour"
      />
      <div className="flex flex-wrap gap-3 text-xs">
        {RISK_LABELS.map((label, i) => (
          <span key={label}>
            <span className="mr-1 inline-block h-2 w-2 rounded-full" style={{ background: RISK_COLORS[i] }} />
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}
