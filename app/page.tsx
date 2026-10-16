"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import ForecastSlider from "./components/ForecastSlider";
import RouteList from "./components/RouteList";
import type { Plan, Trip } from "./types";

const TripForm = dynamic(() => import("./components/TripForm"), { ssr: false });
const RouteMap = dynamic(() => import("./components/RouteMap"), { ssr: false });

export default function Home() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [selected, setSelected] = useState(0);
  const [hour, setHour] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function planTrip(trip: Trip) {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/plan", { method: "POST", body: JSON.stringify(trip) });
      const data = await response.json().catch(() => ({ error: "Backend is not reachable" }));
      if (!response.ok) throw new Error(data.error);
      setPlan(data);
      setSelected(data.best);
      setHour(0);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    }
    setLoading(false);
  }

  return (
    <main className="flex h-screen flex-col md:flex-row">
      <aside className="w-full space-y-4 overflow-y-auto p-4 md:w-[400px]">
        <h1 className="text-lg font-semibold">Weather-Aware Truck Routing</h1>
        <TripForm loading={loading} onSubmit={planTrip} />
        {error && <p className="rounded bg-red-50 p-2 text-sm text-red-700">{error}</p>}
        {plan && <RouteList plan={plan} selected={selected} onSelect={setSelected} />}
      </aside>
      <section className="relative min-h-[400px] flex-1">
        <RouteMap plan={plan} selected={selected} hour={hour} onSelect={setSelected} />
        {plan && (
          <div className="absolute bottom-6 left-1/2 z-[1000] w-[min(480px,90%)] -translate-x-1/2">
            <ForecastSlider start={plan.heatmap.start} hour={hour} onChange={setHour} />
          </div>
        )}
      </section>
    </main>
  );
}
