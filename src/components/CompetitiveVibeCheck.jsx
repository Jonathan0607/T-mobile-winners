import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const CompetitiveVibeCheck = ({ competitiveData }) => {
  const chartData = competitiveData.competitors.map(comp => ({
    name: comp.name,
    score: comp.score,
    fill: comp.color
  }));

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-white mb-6">Competitive Vibe Check</h2>
      
      <div className="h-64 mb-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <XAxis
              dataKey="name"
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF' }}
            />
            <YAxis
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF' }}
              domain={[75, 90]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '6px',
                color: '#FFFFFF'
              }}
            />
            <Bar dataKey="score" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700">
        <p className="text-sm text-gray-300">
          <span className="font-semibold text-white">{competitiveData.weakness.competitor} Weakness:</span>{' '}
          {competitiveData.weakness.issue}
        </p>
      </div>
    </div>
  );
};

export default CompetitiveVibeCheck;
