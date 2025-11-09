// Mock data for T-Mobile Vibe Check Dashboard

export const summaryData = {
  chi_score: 85.2,
  trend: {
    value: -1.5,
    direction: 'down',
    period: 'Last Hour'
  },
  action_cards: [
    {
      id: 1,
      priority: 'Critical',
      title: 'Network Outage Detected',
      team: 'Network Operations',
      insight: 'Multiple towers reporting downtime in the Northeast region. Immediate attention required.',
      location: 'Northeast Region'
    },
    {
      id: 2,
      priority: 'High',
      title: 'Customer Satisfaction Drop',
      team: 'Customer Experience',
      insight: 'CSAT scores decreased by 8% in the past 24 hours. Review recent support interactions.',
      location: 'National'
    }
  ]
};

// 24-hour trend data for line chart
export const trendData = [
  { hour: '00:00', value: 86.5 },
  { hour: '04:00', value: 87.0 },
  { hour: '08:00', value: 86.8 },
  { hour: '12:00', value: 87.2 },
  { hour: '16:00', value: 86.9 },
  { hour: '20:00', value: 85.7 },
  { hour: '24:00', value: 85.2 }
];

// Competitive comparison data
export const competitiveData = {
  competitors: [
    { name: 'T-Mobile', score: 85.2, color: '#E20074' },
    { name: 'AT&T', score: 87.7, color: '#6B7280' },
    { name: 'Verizon', score: 81.2, color: '#6B7280' }
  ],
  weakness: {
    competitor: 'Verizon',
    issue: 'Expensive Plans'
  }
};

// Heat map data (mock city locations)
export const heatMapData = [
  { city: 'NYC', x: 75, y: 45, intensity: 'high', velocity: 'high' },
  { city: 'LA', x: 25, y: 60, intensity: 'medium', velocity: 'medium' },
  { city: 'MIA', x: 70, y: 80, intensity: 'high', velocity: 'high' },
  { city: 'CHI', x: 55, y: 40, intensity: 'low', velocity: 'low' },
  { city: 'SEA', x: 20, y: 25, intensity: 'medium', velocity: 'medium' }
];
