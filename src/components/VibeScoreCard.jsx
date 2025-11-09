import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from 'recharts';

const VibeScoreCard = ({ score, trend, trendData }) => {
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <div className="flex flex-col items-center">
        {/* CHI Score with Magenta Border */}
        <div className="relative w-48 h-48 flex items-center justify-center mb-4">
          <svg className="absolute inset-0 w-full h-full transform -rotate-90">
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              className="text-gray-700"
            />
            <circle
              cx="96"
              cy="96"
              r="88"
              stroke="currentColor"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${(score / 100) * 552} 552`}
              className="text-magenta transition-all duration-500"
            />
          </svg>
          <div className="text-center z-10">
            <div className="text-5xl font-bold text-white">{score}</div>
            <div className="text-sm text-gray-400 mt-1">CHI Score</div>
          </div>
        </div>

        {/* Trend Indicator */}
        <div className="flex items-center gap-2 mb-4">
          <svg
            className="w-5 h-5 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
          <span className="text-red-500 font-semibold">
            {Math.abs(trend.value).toFixed(1)} vs {trend.period}
          </span>
        </div>

        {/* Mini Line Chart */}
        <div className="w-full h-32 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData}>
              <XAxis
                dataKey="hour"
                stroke="#6B7280"
                tick={{ fill: '#9CA3AF', fontSize: 10 }}
                interval="preserveStartEnd"
              />
              <YAxis
                stroke="#6B7280"
                tick={{ fill: '#9CA3AF', fontSize: 10 }}
                domain={[80, 90]}
                hide
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '6px',
                  color: '#FFFFFF'
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#E20074"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: '#E20074' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default VibeScoreCard;
