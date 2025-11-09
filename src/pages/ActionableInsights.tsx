import { useEffect, useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';

interface TriageQueueItem {
  id: string;
  title: string;
  velocity: number;
  time_since_alert_h: number;
  status: string;
  owner_team: string;
  resolution_summary?: string;
}

interface CauseBreakdown {
  name: string;
  value: number;
  color: string;
}

interface TriageData {
  kpis: {
    critical_count: number;
    mttr_h: number;
    resolved_24h: number;
  };
  queue: TriageQueueItem[];
  cause_breakdown: CauseBreakdown[];
}

export default function ActionableInsights() {
  const [data, setData] = useState<TriageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('http://localhost:5001/api/vibecheck/triage_queue');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jsonData = await response.json();
        setData(jsonData);
      } catch (err) {
        const errorMessage = err instanceof Error 
          ? err.message 
          : 'An error occurred';
        
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Load failed')) {
          setError('Unable to connect to Flask server. Please make sure the Flask server is running on http://localhost:5001');
        } else {
          setError(`Error: ${errorMessage}`);
        }
        console.error('Error fetching triage data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusColor = (status: string): string => {
    switch (status.toLowerCase()) {
      case 'new':
        return '#FFC300'; // Yellow
      case 'in progress':
        return '#3B82F6'; // Blue
      case 'resolved':
        return '#10B981'; // Green
      default:
        return '#9CA3AF'; // Gray
    }
  };

  const getVelocityColor = (velocity: number): string => {
    if (velocity > 8.0) {
      return '#D62828'; // Bright red
    }
    return '#CCCCCC'; // Default gray
  };

  const getTimeSinceAlertColor = (time: number): string => {
    if (time > 4.0) {
      return '#D62828'; // Bold red
    }
    return '#CCCCCC'; // Default gray
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 min-h-screen bg-[#1A1A1A] text-white">
        <h1 className="text-3xl font-bold mb-8 ml-8">Actionable Insights</h1>
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <div className="text-red-500 text-xl mb-4">Error: {error}</div>
          <div className="text-[#CCCCCC] text-sm">
            <p className="mb-2">To fix this issue:</p>
            <ol className="list-decimal list-inside space-y-1 ml-4">
              <li>Make sure the Flask server is running: <code className="bg-[#1A1A1A] px-2 py-1 rounded">python app.py</code></li>
              <li>Verify the Flask server is accessible at <code className="bg-[#1A1A1A] px-2 py-1 rounded">http://localhost:5001</code></li>
              <li>Check that the endpoint <code className="bg-[#1A1A1A] px-2 py-1 rounded">/api/vibecheck/triage_queue</code> exists</li>
              <li>Ensure CORS is enabled in the Flask app</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  // Filter resolved items for the learning loop
  const resolvedItems = data.queue.filter(item => item.status.toLowerCase() === 'resolved');

  return (
    <div className="p-8 min-h-screen bg-[#1A1A1A] text-white">
      <h1 className="text-3xl font-bold mb-8 ml-8">Actionable Insights</h1>

      {/* Row 1: KPIs & Triage Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Critical Issues KPI */}
        <div className="bg-[#2C2C2C] rounded-xl p-6 border-l-4 border-[#E20074]">
          <h3 className="text-sm text-[#9CA3AF] mb-2">Critical Issues</h3>
          <p className="text-4xl font-bold text-white">{data.kpis.critical_count}</p>
        </div>

        {/* MTTR KPI */}
        <div className="bg-[#2C2C2C] rounded-xl p-6 border-l-4 border-[#E20074]">
          <h3 className="text-sm text-[#9CA3AF] mb-2">MTTR (Last 7 Days)</h3>
          <p className="text-4xl font-bold text-white">{data.kpis.mttr_h.toFixed(1)}h</p>
        </div>

        {/* Issues Resolved KPI */}
        <div className="bg-[#2C2C2C] rounded-xl p-6 border-l-4 border-[#E20074]">
          <h3 className="text-sm text-[#9CA3AF] mb-2">Issues Resolved (24 Hrs)</h3>
          <p className="text-4xl font-bold text-white">{data.kpis.resolved_24h}</p>
        </div>
      </div>

      {/* Row 2: Triage Queue */}
      <div className="mb-8">
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <h2 className="text-2xl font-semibold mb-4">Active Triage Queue (High Velocity Alerts)</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#555555]">
                  <th className="text-left py-3 px-4 text-white font-semibold">Title</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Velocity</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Time Since Alert (h)</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Status</th>
                  <th className="text-left py-3 px-4 text-white font-semibold">Owner Team</th>
                </tr>
              </thead>
              <tbody>
                {data.queue.map((item) => (
                  <tr 
                    key={item.id} 
                    className="border-b border-[#404040] hover:bg-[#3C3C3C] transition-colors"
                  >
                    <td className="py-3 px-4 text-[#CCCCCC] font-medium">{item.title}</td>
                    <td 
                      className="py-3 px-4 text-center font-semibold"
                      style={{ 
                        color: getVelocityColor(item.velocity),
                        backgroundColor: item.velocity > 8.0 ? 'rgba(214, 40, 40, 0.1)' : 'transparent'
                      }}
                    >
                      {item.velocity.toFixed(1)}
                    </td>
                    <td 
                      className="py-3 px-4 text-center font-semibold"
                      style={{ color: getTimeSinceAlertColor(item.time_since_alert_h) }}
                    >
                      {item.time_since_alert_h.toFixed(1)}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className="px-3 py-1 rounded-full text-sm font-medium"
                        style={{
                          backgroundColor: getStatusColor(item.status),
                          color: '#FFFFFF'
                        }}
                      >
                        {item.status}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 bg-[#3C3C3C] rounded text-[#CCCCCC] text-sm">
                        {item.owner_team}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Row 3: Analysis & Learning */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Column 1: Root Cause Breakdown */}
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <h2 className="text-2xl font-semibold mb-4">Systemic Root Cause Breakdown</h2>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={data.cause_breakdown as any}
                cx="50%"
                cy="50%"
                labelLine={true}
                label={(entry: any) => {
                  const percent = ((entry.percent as number) * 100).toFixed(0);
                  return `${percent}%`;
                }}
                outerRadius={100}
                innerRadius={20}
                fill="#8884d8"
                dataKey="value"
              >
                {data.cause_breakdown.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#2C2C2C', 
                  border: '1px solid #555555',
                  borderRadius: '8px',
                  color: '#FFFFFF',
                  fontSize: '14px',
                  fontFamily: 'Arial, sans-serif'
                }}
                itemStyle={{ color: '#FFFFFF', fontSize: '14px', fontFamily: 'Arial, sans-serif' }}
                labelStyle={{ color: '#FFFFFF', fontSize: '14px', fontFamily: 'Arial, sans-serif' }}
                formatter={(value: any, name: any) => [`${value}`, name]}
                labelFormatter={(label) => <span style={{ color: '#FFFFFF', fontSize: '14px', fontFamily: 'Arial, sans-serif' }}>{label}</span>}
              />
              <Legend 
                wrapperStyle={{ color: '#FFFFFF', paddingTop: '20px', fontSize: '14px', fontFamily: 'Arial, sans-serif' }}
                iconType="circle"
                formatter={(value) => <span style={{ color: '#FFFFFF', fontSize: '14px', fontFamily: 'Arial, sans-serif' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Column 2: Learning Loop */}
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <h2 className="text-2xl font-semibold mb-4">Learnings from Resolved Issues</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#555555]">
                  <th className="text-left py-3 px-4 text-white font-semibold">Title</th>
                  <th className="text-left py-3 px-4 text-white font-semibold">Owner</th>
                  <th className="text-left py-3 px-4 text-white font-semibold">Resolution Summary</th>
                </tr>
              </thead>
              <tbody>
                {resolvedItems.length > 0 ? (
                  resolvedItems.map((item) => (
                    <tr 
                      key={item.id} 
                      className="border-b border-[#404040] hover:bg-[#3C3C3C] transition-colors"
                    >
                      <td className="py-3 px-4 text-[#CCCCCC] font-medium">{item.title}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-1 bg-[#3C3C3C] rounded text-[#CCCCCC] text-sm">
                          {item.owner_team}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-[#CCCCCC] text-sm">
                        {item.resolution_summary || 'No summary available'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="py-4 px-4 text-center text-[#9CA3AF]">
                      No resolved issues to display
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

