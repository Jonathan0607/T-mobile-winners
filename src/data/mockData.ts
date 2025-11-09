export interface ActionCard {
  id: string;
  team: string;
  priority: "Critical" | "High";
  title: string;
  insight: string;
  color: string;
}

export interface MockSummary {
  chi_score: number;
  chi_trend: number;
  trend_direction: "up" | "down";
  trend_period: string;
  action_cards: ActionCard[];
}

export interface CompetitiveData {
  carrier: string;
  score: number;
}

export interface HeatmapData {
  city: string;
  lat: number;
  lon: number;
  intensity: "high" | "medium" | "low";
  velocity: "high" | "medium" | "low";
  issues: number;
  predicted?: boolean;
}

export interface TrendDataPoint {
  time: Date;
  score: number;
}

export const MOCK_SUMMARY: MockSummary = {
  chi_score: 85.2,
  chi_trend: -1.5,
  trend_direction: "down",
  trend_period: "Last Hour",
  action_cards: [
    {
      id: "A101",
      team: "Network Engineering",
      priority: "Critical",
      title: "Investigate 5G outage in Miami",
      insight: "40% spike in 'slow data' complaints in zip 33139 over 1hr.",
      color: "#D62828",
    },
    {
      id: "A102",
      team: "Social Media Support",
      priority: "High",
      title: "Draft response to #SlowMagenta trend",
      insight: "Sentiment velocity shows high risk of negative virality in 2 hours.",
      color: "#FFC300",
    },
    {
      id: "A103",
      team: "Customer Service",
      priority: "High",
      title: "Address billing complaints in Seattle area",
      insight: "35% increase in billing-related support tickets from Seattle metro in past 4 hours.",
      color: "#FFC300",
    },
  ],
};

export const MOCK_COMPETITIVE_DATA: CompetitiveData[] = [
  { carrier: "T-Mobile (85.2)", score: 85.2 },
  { carrier: "AT&T (87.7)", score: 87.7 },
  { carrier: "Verizon (81.2)", score: 81.2 },
];

export const PRESENT_HEATMAP_DATA: HeatmapData[] = [
  { city: "New York", lat: 40.7128, lon: -74.0060, intensity: "high", velocity: "high", issues: 45 },
  { city: "Los Angeles", lat: 34.0522, lon: -118.2437, intensity: "medium", velocity: "medium", issues: 28 },
  { city: "Miami", lat: 25.7617, lon: -80.1918, intensity: "high", velocity: "high", issues: 52 },
  { city: "Chicago", lat: 41.8781, lon: -87.6298, intensity: "low", velocity: "low", issues: 12 },
  { city: "Seattle", lat: 47.6062, lon: -122.3321, intensity: "medium", velocity: "medium", issues: 19 },
  { city: "Dallas", lat: 32.7767, lon: -96.7970, intensity: "medium", velocity: "medium", issues: 22 },
  { city: "Houston", lat: 29.7604, lon: -95.3698, intensity: "low", velocity: "low", issues: 15 },
  { city: "Atlanta", lat: 33.7490, lon: -84.3880, intensity: "high", velocity: "high", issues: 38 },
];

export const PREDICTIVE_HEATMAP_DATA: HeatmapData[] = [
  { city: "New York", lat: 40.7128, lon: -74.0060, intensity: "high", velocity: "high", issues: 58, predicted: true },
  { city: "Los Angeles", lat: 34.0522, lon: -118.2437, intensity: "high", velocity: "high", issues: 42, predicted: true },
  { city: "Miami", lat: 25.7617, lon: -80.1918, intensity: "high", velocity: "high", issues: 65, predicted: true },
  { city: "Chicago", lat: 41.8781, lon: -87.6298, intensity: "medium", velocity: "medium", issues: 25, predicted: true },
  { city: "Seattle", lat: 47.6062, lon: -122.3321, intensity: "high", velocity: "high", issues: 32, predicted: true },
  { city: "Dallas", lat: 32.7767, lon: -96.7970, intensity: "medium", velocity: "medium", issues: 28, predicted: true },
  { city: "Houston", lat: 29.7604, lon: -95.3698, intensity: "medium", velocity: "medium", issues: 22, predicted: true },
  { city: "Atlanta", lat: 33.7490, lon: -84.3880, intensity: "high", velocity: "high", issues: 48, predicted: true },
  { city: "Phoenix", lat: 33.4484, lon: -112.0740, intensity: "medium", velocity: "medium", issues: 18, predicted: true },
  { city: "Denver", lat: 39.7392, lon: -104.9903, intensity: "low", velocity: "low", issues: 14, predicted: true },
];

export function generateTrendData(): TrendDataPoint[] {
  const hours: TrendDataPoint[] = [];
  const now = new Date();
  const baseScore = 85.2;

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    // Add some realistic variation
    const value = baseScore + Math.sin(i * Math.PI / 12) * 3 + (Math.random() - 0.5) * 1;
    const score = Math.max(70, Math.min(95, value));
    hours.push({ time, score });
  }

  return hours;
}

