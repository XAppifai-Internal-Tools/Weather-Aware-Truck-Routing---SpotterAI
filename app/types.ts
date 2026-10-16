export type Checkpoint = {
  lat: number;
  lon: number;
  mile: number;
  miles: number;
  eta: string;
  wind: number;
  rain: number;
  snow: number;
  risk: number;
};

export type Route = {
  name: string;
  coords: [number, number][];
  miles: number;
  hours: number;
  checkpoints: Checkpoint[];
  no_travel_miles: number;
  severe_miles: number;
  high_miles: number;
  avg_risk: number;
  worst_risk: number;
};

export type Heatmap = {
  start: string;
  size: number;
  cells: { lat: number; lon: number; risk: (number | null)[] }[];
};

export type Plan = { routes: Route[]; best: number; heatmap: Heatmap };

export type Trip = {
  origin: string;
  destination: string;
  departure: string;
  weight: number;
  interval: number;
};
