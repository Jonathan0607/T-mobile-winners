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

