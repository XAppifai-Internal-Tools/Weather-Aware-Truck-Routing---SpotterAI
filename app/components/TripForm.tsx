"use client";

import { FormEvent } from "react";
import type { Trip } from "../types";

function nextHour() {
  const date = new Date();
  date.setHours(date.getHours() + 1, 0, 0, 0);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:00`;
}

const input = "w-full rounded border border-zinc-300 px-3 py-2 text-sm";

export default function TripForm({ loading, onSubmit }: { loading: boolean; onSubmit: (trip: Trip) => void }) {
  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    onSubmit({
      origin: String(form.get("origin")),
      destination: String(form.get("destination")),
      departure: new Date(String(form.get("departure"))).toISOString(),
      weight: Number(form.get("weight")),
      interval: Number(form.get("interval")),
    });
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <input name="origin" placeholder="Origin, e.g. Chicago, IL" required className={input} />
      <input name="destination" placeholder="Destination, e.g. St. Louis, MO" required className={input} />
      <label className="block text-xs text-zinc-500">
        Departure
        <input name="departure" type="datetime-local" defaultValue={nextHour()} required className={input} />
      </label>
      <div className="flex gap-3">
        <label className="block flex-1 text-xs text-zinc-500">
          Load weight (lb)
          <input name="weight" type="number" min="1" step="1" defaultValue="35000" required className={input} />
        </label>
        <label className="block flex-1 text-xs text-zinc-500">
          Weather every
          <select name="interval" defaultValue="25" className={input}>
            <option value="10">10 miles</option>
            <option value="25">25 miles</option>
            <option value="50">50 miles</option>
          </select>
        </label>
      </div>
      <button disabled={loading} className="w-full rounded bg-zinc-900 py-2 text-sm font-medium text-white disabled:opacity-50">
        {loading ? "Checking routes and weather..." : "Find safest route"}
      </button>
    </form>
  );
}
