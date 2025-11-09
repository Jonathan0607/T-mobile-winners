import { MOCK_SUMMARY } from '../data/mockData';

interface VibeScoreCardProps {
  isSidebarOpen: boolean;
}

export default function VibeScoreCard({ isSidebarOpen }: VibeScoreCardProps) {
  const score = MOCK_SUMMARY.chi_score;
  const percentage = score / 100.0;
  
  // Scale up when sidebar is closed - use CSS transform for smooth transition
  const scaleFactor = isSidebarOpen ? 1 : 1.25;
  const baseRadius = 100;
  const baseCircleSize = 240;
  const radius = baseRadius;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - percentage);

  const trendValue = Math.abs(MOCK_SUMMARY.chi_trend);
  const trendPeriod = MOCK_SUMMARY.trend_period;
  const isPositive = MOCK_SUMMARY.chi_trend > 0 || MOCK_SUMMARY.trend_direction === "up";
  const trendColor = isPositive ? "#10B981" : "#D62828"; // Green for positive, red for negative
  const trendArrow = isPositive ? "↑" : "↓";

  // Shift down when sidebar is closed
  const trendMarginTop = isSidebarOpen ? "1rem" : "3rem";
  // Increase font size when sidebar is closed
  const trendFontSize = isSidebarOpen ? 16 : 22; // Scale up from 16px to 22px
  const trendArrowSize = isSidebarOpen ? "text-xl" : "text-2xl"; // Scale up arrow size

  return (
    <div className="flex flex-col items-center justify-center h-full">
      {/* Circular Progress Indicator */}
      <div 
        className="relative transition-transform duration-300 ease-in-out" 
        style={{ 
          width: baseCircleSize, 
          height: baseCircleSize, 
          margin: '0 auto',
          transform: `scale(${scaleFactor})`,
          transformOrigin: 'center center'
        }}
      >
        <svg
          width={baseCircleSize}
          height={baseCircleSize}
          style={{ transform: 'rotate(-90deg)' }}
        >
          <circle
            cx={baseCircleSize / 2}
            cy={baseCircleSize / 2}
            r={radius}
            stroke="#404040"
            strokeWidth={16}
            fill="none"
          />
          <circle
            cx={baseCircleSize / 2}
            cy={baseCircleSize / 2}
            r={radius}
            stroke="#E20074"
            strokeWidth={16}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
          />
        </svg>
        <div
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center w-full transition-all duration-300 ease-in-out"
        >
          <div className={`font-bold text-white transition-all duration-300 ease-in-out`} style={{ fontSize: `${64}px` }}>
            {score}
          </div>
          <div className={`text-[#9CA3AF] mt-1 transition-all duration-300 ease-in-out`} style={{ fontSize: `${16}px` }}>
            CHI Score
          </div>
        </div>
      </div>

      {/* Trend Indicator */}
      <div 
        className="flex items-center justify-center gap-2 font-semibold transition-all duration-300 ease-in-out" 
        style={{ 
          fontSize: `${trendFontSize}px`, 
          color: trendColor,
          marginTop: trendMarginTop,
          marginBottom: '1rem'
        }}
      >
        <span className={trendArrowSize}>{trendArrow}</span>
        <span>
          {trendValue} vs {trendPeriod}
        </span>
      </div>
    </div>
  );
}

