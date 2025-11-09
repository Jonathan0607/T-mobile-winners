const PredictiveIssueHeatMap = ({ heatMapData }) => {
  const getCircleColor = (velocity) => {
    return velocity === 'high' ? '#EF4444' : '#E20074';
  };

  const getCircleSize = (intensity) => {
    if (intensity === 'high') return 16;
    if (intensity === 'medium') return 12;
    return 8;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-white mb-6">Predictive Issue Heat Map</h2>
      
      {/* Map Container */}
      <div className="relative w-full h-64 bg-gray-900 rounded-lg border border-gray-700 mb-4 overflow-hidden">
        <svg viewBox="0 0 100 100" className="w-full h-full" preserveAspectRatio="none">
          {/* Grid lines */}
          <defs>
            <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
              <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#374151" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100" height="100" fill="url(#grid)" />
          
          {/* City markers */}
          {heatMapData.map((city, index) => (
            <g key={index}>
              <circle
                cx={city.x}
                cy={city.y}
                r={getCircleSize(city.intensity) / 2}
                fill={getCircleColor(city.velocity)}
                opacity="0.8"
              />
              <text
                x={city.x}
                y={city.y}
                dx="1.5"
                dy="0.5"
                fill="#FFFFFF"
                fontSize="3"
                fontWeight="bold"
              >
                {city.city}
              </text>
            </g>
          ))}
        </svg>
      </div>
      
      {/* Legend */}
      <div className="flex items-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded-full"></div>
          <span className="text-gray-300">Velocity: High (Red)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full" style={{ backgroundColor: '#E20074' }}></div>
          <span className="text-gray-300">Velocity: Low (Magenta)</span>
        </div>
      </div>
    </div>
  );
};

export default PredictiveIssueHeatMap;
