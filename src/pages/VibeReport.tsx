import { useEffect, useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface SentimentPolarity {
  name: string;
  value: number;
  color: string;
}

interface SentimentBySource {
  source: string;
  Positive: number;
  Neutral: number;
  Negative: number;
}

interface TopTopic {
  topic: string;
  volume: number;
  nss: number;
}

interface DelightFeedItem {
  snippet: string;
  source: string;
  emotion: string;
}

interface VibeReportData {
  sentiment_polarity: SentimentPolarity[];
  sentiment_by_source: SentimentBySource[];
  top_topics: TopTopic[];
  delight_feed: DelightFeedItem[];
}

export default function VibeReport() {
  const [data, setData] = useState<VibeReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('http://localhost:5001/api/vibecheck/vibe_report');
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
        console.error('Error fetching vibe report data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getNSSColor = (nss: number): string => {
    if (nss > 0) {
      return '#10B981'; // Green for positive/good NSS
    } else if (nss < 0) {
      return '#D62828'; // Red for negative/bad NSS
    }
    return '#CCCCCC'; // Gray for neutral (0)
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
        <h1 className="text-3xl font-bold mb-8 ml-8">Vibe Report: Internal Analysis</h1>
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <div className="text-red-500 text-xl mb-4">Error: {error}</div>
          <div className="text-[#CCCCCC] text-sm">
            <p className="mb-2">To fix this issue:</p>
            <ol className="list-decimal list-inside space-y-1 ml-4">
              <li>Make sure the Flask server is running: <code className="bg-[#1A1A1A] px-2 py-1 rounded">python app.py</code></li>
              <li>Verify the Flask server is accessible at <code className="bg-[#1A1A1A] px-2 py-1 rounded">http://localhost:5001</code></li>
              <li>Check that the endpoint <code className="bg-[#1A1A1A] px-2 py-1 rounded">/api/vibecheck/vibe_report</code> exists</li>
              <li>Ensure CORS is enabled in the Flask app</li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-8 min-h-screen bg-[#1A1A1A] text-white">
        <h1 className="text-3xl font-bold mb-8 ml-8">Vibe Report: Internal Analysis</h1>
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <div className="text-[#9CA3AF] text-center">No data available.</div>
        </div>
      </div>
    );
  }

  // Validate data structure and provide safe defaults
  const sentimentPolarity = Array.isArray(data.sentiment_polarity) ? data.sentiment_polarity : [];
  const sentimentBySource = Array.isArray(data.sentiment_by_source) ? data.sentiment_by_source : [];
  const topTopics = Array.isArray(data.top_topics) ? data.top_topics : [];
  const delightFeed = Array.isArray(data.delight_feed) ? data.delight_feed : [];

  // Prepare data for stacked bar chart
  const barChartData = sentimentBySource.map(item => ({
    source: item.source || 'Unknown',
    Positive: item.Positive || 0,
    Neutral: item.Neutral || 0,
    Negative: item.Negative || 0,
  }));

  return (
    <div className="p-8 min-h-screen bg-[#1A1A1A] text-white">
      <h1 className="text-3xl font-bold mb-8 ml-8">Vibe Report: Internal Analysis</h1>

      {/* Row 1: Distribution - grid-cols-3 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8 items-stretch">
        {/* Col 1: Sentiment Polarity Pie Chart */}
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4 text-center">Sentiment Polarity</h2>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={sentimentPolarity as any}
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
                {sentimentPolarity.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || "#8884d8"} />
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
                formatter={(value: any, name: any) => [`${value}%`, name]}
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

        {/* Col 2 & 3: Sentiment by Source Stacked Bar Chart */}
        <div className="lg:col-span-2 bg-[#2C2C2C] rounded-xl p-6 flex flex-col h-full">
          <h2 className="text-xl font-semibold mb-4 text-center">Sentiment by Source</h2>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barChartData} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#404040" />
                <XAxis 
                  dataKey="source" 
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                />
                <YAxis 
                  stroke="#9CA3AF"
                  tick={{ fill: '#9CA3AF' }}
                />
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
                />
                <Legend 
                  wrapperStyle={{ color: '#FFFFFF', fontSize: '14px', fontFamily: 'Arial, sans-serif' }}
                  iconType="circle"
                  formatter={(value) => <span style={{ color: '#FFFFFF', fontSize: '14px', fontFamily: 'Arial, sans-serif' }}>{value}</span>}
                />
                <Bar dataKey="Positive" stackId="a" fill="#E20074" name="Positive" />
                <Bar dataKey="Neutral" stackId="a" fill="#9CA3AF" name="Neutral" />
                <Bar dataKey="Negative" stackId="a" fill="#D62828" name="Negative" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 2: Topic Analysis - Full Width */}
      <div className="mb-8">
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <h2 className="text-2xl font-semibold mb-4">AI-Analyzed Topics: Pain Points & Delight Drivers</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[#555555]">
                  <th className="text-left py-3 px-4 text-white font-semibold">Topic</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Volume</th>
                  <th className="text-center py-3 px-4 text-white font-semibold">Net Sentiment Score</th>
                </tr>
              </thead>
              <tbody>
                {topTopics.length > 0 ? (
                  topTopics.map((topic, index) => (
                    <tr 
                      key={index} 
                      className="border-b border-[#404040] hover:bg-[#3C3C3C] transition-colors"
                    >
                      <td className="py-3 px-4 text-[#CCCCCC] font-medium">{topic.topic || 'Unknown'}</td>
                      <td className="py-3 px-4 text-[#CCCCCC] text-center">{(topic.volume || 0).toLocaleString()}</td>
                      <td 
                        className="py-3 px-4 font-semibold text-center" 
                        style={{ color: getNSSColor(topic.nss || 0) }}
                      >
                        {topic.nss || 0}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={3} className="py-3 px-4 text-center text-[#9CA3AF]">No topic data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Row 3: Qualitative Insights - grid-cols-3 */}
      <div className="mb-8">
        <div className="bg-[#2C2C2C] rounded-xl p-6">
          <h2 className="text-2xl font-semibold mb-4">Moments of Delight (Top Positive Feedback)</h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {delightFeed.length > 0 ? (
              delightFeed.map((item, index) => (
                <div 
                  key={index}
                  className="border-2 border-[#E20074] rounded-lg p-4 bg-[#1A1A1A]"
                >
                  <p className="text-white mb-2 text-sm">{item.snippet || 'No snippet available'}</p>
                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-[#9CA3AF]">{item.source || 'Unknown'}</span>
                    <span className="text-xs text-[#E20074] font-semibold">{item.emotion || 'Positive'}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-3 text-center text-[#9CA3AF] py-8">No delight feed data available</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

