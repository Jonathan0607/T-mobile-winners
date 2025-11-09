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

export const PRESENT_HEATMAP_DATA: HeatmapData[] = [
  { city: "New York", lat: 40.7128, lon: -74.0060, intensity: "high", velocity: "high", issues: 45 },
  { city: "Los Angeles", lat: 34.0522, lon: -118.2437, intensity: "medium", velocity: "medium", issues: 28 },
  { city: "Chicago", lat: 41.8781, lon: -87.6298, intensity: "medium", velocity: "low", issues: 22 },
  { city: "Houston", lat: 29.7604, lon: -95.3698, intensity: "low", velocity: "medium", issues: 15 },
  { city: "Phoenix", lat: 33.4484, lon: -112.0740, intensity: "high", velocity: "high", issues: 38 },
  { city: "Philadelphia", lat: 39.9526, lon: -75.1652, intensity: "medium", velocity: "low", issues: 19 },
  { city: "San Antonio", lat: 29.4241, lon: -98.4936, intensity: "low", velocity: "low", issues: 12 },
  { city: "San Diego", lat: 32.7157, lon: -117.1611, intensity: "low", velocity: "medium", issues: 14 },
  { city: "Dallas", lat: 32.7767, lon: -96.7970, intensity: "medium", velocity: "high", issues: 25 },
  { city: "San Jose", lat: 37.3382, lon: -121.8863, intensity: "medium", velocity: "medium", issues: 20 },
  { city: "Austin", lat: 30.2672, lon: -97.7431, intensity: "low", velocity: "low", issues: 10 },
  { city: "Jacksonville", lat: 30.3322, lon: -81.6557, intensity: "medium", velocity: "medium", issues: 18 },
  { city: "Miami", lat: 25.7617, lon: -80.1918, intensity: "high", velocity: "high", issues: 42 },
  { city: "Seattle", lat: 47.6062, lon: -122.3321, intensity: "medium", velocity: "low", issues: 21 },
  { city: "Denver", lat: 39.7392, lon: -104.9903, intensity: "low", velocity: "medium", issues: 13 },
];

export const PREDICTIVE_HEATMAP_DATA: HeatmapData[] = [
  { city: "New York", lat: 40.7128, lon: -74.0060, intensity: "high", velocity: "high", issues: 52, predicted: true },
  { city: "Los Angeles", lat: 34.0522, lon: -118.2437, intensity: "high", velocity: "high", issues: 35, predicted: true },
  { city: "Chicago", lat: 41.8781, lon: -87.6298, intensity: "medium", velocity: "medium", issues: 26, predicted: true },
  { city: "Houston", lat: 29.7604, lon: -95.3698, intensity: "medium", velocity: "medium", issues: 20, predicted: true },
  { city: "Phoenix", lat: 33.4484, lon: -112.0740, intensity: "high", velocity: "high", issues: 45, predicted: true },
  { city: "Philadelphia", lat: 39.9526, lon: -75.1652, intensity: "medium", velocity: "medium", issues: 24, predicted: true },
  { city: "San Antonio", lat: 29.4241, lon: -98.4936, intensity: "low", velocity: "low", issues: 15, predicted: true },
  { city: "San Diego", lat: 32.7157, lon: -117.1611, intensity: "medium", velocity: "medium", issues: 18, predicted: true },
  { city: "Dallas", lat: 32.7767, lon: -96.7970, intensity: "high", velocity: "high", issues: 32, predicted: true },
  { city: "San Jose", lat: 37.3382, lon: -121.8863, intensity: "medium", velocity: "high", issues: 25, predicted: true },
  { city: "Austin", lat: 30.2672, lon: -97.7431, intensity: "medium", velocity: "medium", issues: 16, predicted: true },
  { city: "Jacksonville", lat: 30.3322, lon: -81.6557, intensity: "medium", velocity: "medium", issues: 22, predicted: true },
  { city: "Miami", lat: 25.7617, lon: -80.1918, intensity: "high", velocity: "high", issues: 48, predicted: true },
  { city: "Seattle", lat: 47.6062, lon: -122.3321, intensity: "medium", velocity: "medium", issues: 28, predicted: true },
  { city: "Denver", lat: 39.7392, lon: -104.9903, intensity: "medium", velocity: "low", issues: 17, predicted: true },
];

