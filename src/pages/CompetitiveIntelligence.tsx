import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface HistoricalVibeGap {
  date: string;
  T_Mobile: number;
  ATT: number;
  Verizon: number;
}

interface FeatureComparison {
  'Feature/Service': string;
  T_Mobile: string;
  ATT: string;
  Verizon: string;
}

interface CompetitorWeakness {
  competitor: string;
  weakness: string;
  action_suggestion: string;
}

interface TMobileCritique {
  critique: string;
  source_impact: string;
  team_suggestion: string;
}

interface CompetitiveData {
  historical_vibe_gap: HistoricalVibeGap[];
  feature_comparison_matrix: FeatureComparison[];
  comp_weaknesses: CompetitorWeakness[];
  tmobile_critiques: TMobileCritique[];
}

export default function CompetitiveAnalysis() {
  const [data, setData] = useState<CompetitiveData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('http://localhost:5001/api/vibecheck/competitive');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jsonData = await response.json();
        setData(jsonData);
      } catch (err) {
        const errorMessage = err instanceof Error 
          ? err.message 
          : 'An error occurred';
        
        // Check if it's a network error (Flask server not running)
        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Load failed')) {
          setError('Unable to connect to Flask server. Please make sure the Flask server is running on http://localhost:5001');
        } else {
          setError(`Error: ${errorMessage}`);
        }
        console.error('Error fetching competitive data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getSentimentColor = (sentiment: string): string => {
    if (sentiment.toLowerCase().includes('positive') || sentiment.toLowerCase().includes('strong positive')) {
      return '#10B981'; // Green
    } else if (sentiment.toLowerCase().includes('negative')) {
      return '#EF4444'; // Red
    } else if (sentiment.toLowerCase().includes('mixed')) {
      return '#F59E0B'; // Yellow/Orange
    }
    return '#9CA3AF'; // Gray for neutral
  };

  const getSentimentIcon = (sentiment: string): string => {
    if (sentiment.toLowerCase().includes('positive') || sentiment.toLowerCase().includes('strong positive')) {
      return '✓';
    } else if (sentiment.toLowerCase().includes('negative')) {
      return '✗';
    } else if (sentiment.toLowerCase().includes('mixed')) {
      return '~';
    }
    return '○';
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
        <h1 className="text-3xl font-bold mb-8">Competitive Intelligence</h1>
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <div className="text-red-500 text-xl mb-4">Error: {error}</div>
          <div className="text-[#CCCCCC] text-sm">
            <p className="mb-2">To fix this issue:</p>
            <ol className="list-decimal list-inside space-y-1 ml-4">
              <li>Make sure the Flask server is running: <code className="bg-[#1A1A1A] px-2 py-1 rounded">python app.py</code></li>
              <li>Verify the Flask server is accessible at <code className="bg-[#1A1A1A] px-2 py-1 rounded">http://localhost:5001</code></li>
              <li>Check that the endpoint <code className="bg-[#1A1A1A] px-2 py-1 rounded">/api/vibecheck/competitive</code> exists</li>
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

  return (
    <div className="p-8 min-h-screen bg-[#1A1A1A] text-white">
      <h1 className="text-3xl font-bold mb-8 ml-8">Competitive Analysis</h1>

      {/* Row 1: Vibe Gap Trends (Full Width) */}
      <div className="mb-8">
        <div className="bg-[#2C2C2C] rounded-xl p-6 w-full">
          <h2 className="text-2xl font-semibold mb-6">Vibe Gap Trends</h2>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={data.historical_vibe_gap}>
              <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
              <XAxis 
                dataKey="date" 
                stroke="#9CA3AF"
                tick={{ fill: '#9CA3AF' }}
              />
              <YAxis 
                stroke="#9CA3AF"
                tick={{ fill: '#9CA3AF' }}
                domain={['dataMin - 10', 'dataMax + 10']}
                label={{ value: 'CHI Score', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#9CA3AF' } }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#2C2C2C', 
                  border: '1px solid #555555',
                  borderRadius: '8px',
                  color: '#FFFFFF'
                }}
              />
              <Legend 
                wrapperStyle={{ color: '#FFFFFF' }}
              />
              <Line 
                type="monotone" 
                dataKey="T_Mobile" 
                stroke="#E20074" 
                strokeWidth={3}
                name="T-Mobile"
                dot={{ fill: '#E20074', r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="ATT" 
                stroke="#FFC300" 
                strokeWidth={2}
                name="AT&T"
                dot={{ fill: '#FFC300', r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="Verizon" 
                stroke="#CCCCCC" 
                strokeWidth={2}
                name="Verizon"
                dot={{ fill: '#CCCCCC', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 2: Feature & Market Analysis */}
      <div className="mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Feature Comparison Table */}
          <div className="bg-[#2C2C2C] rounded-xl p-6">
            <h2 className="text-2xl font-semibold mb-4">AI-Analyzed Feature Sentiment Comparison</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#555555]">
                    <th className="text-left py-3 px-4 text-white font-semibold">Feature/Service</th>
                    <th className="text-left py-3 px-4 text-white font-semibold">T-Mobile</th>
                    <th className="text-left py-3 px-4 text-white font-semibold">AT&T</th>
                    <th className="text-left py-3 px-4 text-white font-semibold">Verizon</th>
                  </tr>
                </thead>
                <tbody>
                  {data.feature_comparison_matrix.map((feature, index) => (
                    <tr key={index} className="border-b border-[#404040] hover:bg-[#3C3C3C]">
                      <td className="py-3 px-4 text-white">{feature['Feature/Service']}</td>
                      <td className="py-3 px-4">
                        <span 
                          style={{ color: getSentimentColor(feature.T_Mobile) }}
                          className="font-medium"
                        >
                          {getSentimentIcon(feature.T_Mobile)} {feature.T_Mobile}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span 
                          style={{ color: getSentimentColor(feature.ATT) }}
                          className="font-medium"
                        >
                          {getSentimentIcon(feature.ATT)} {feature.ATT}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span 
                          style={{ color: getSentimentColor(feature.Verizon) }}
                          className="font-medium"
                        >
                          {getSentimentIcon(feature.Verizon)} {feature.Verizon}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Competitor Weaknesses Cards */}
          <div className="bg-[#2C2C2C] rounded-xl p-6">
            <h2 className="text-2xl font-semibold mb-4">Competitor Weaknesses</h2>
            <div className="space-y-4">
              {data.comp_weaknesses.map((weakness, index) => (
                <div 
                  key={index}
                  className="border-2 border-[#FFC300] rounded-lg p-4 bg-[#2C2C2C]"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-[#FFC300]">
                      {weakness.competitor}
                    </h3>
                  </div>
                  <p className="text-[#CCCCCC] mb-3">{weakness.weakness}</p>
                  <div className="bg-[#1A1A1A] rounded p-3">
                    <p className="text-sm text-white">
                      <span className="font-semibold text-[#E20074]">Action:</span> {weakness.action_suggestion}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}

