import { useEffect, useState } from 'react';

interface VibeScoreCardProps {
  isSidebarOpen: boolean;
}

interface SummaryData {
  chi_score: number;
  chi_trend: number;
  trend_direction: string;
  trend_period: string;
}

export default function VibeScoreCard({ isSidebarOpen }: VibeScoreCardProps) {
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5001/api/vibecheck/summary');
        if (!response.ok) {
          throw new Error('Failed to fetch summary data');
        }
        const jsonData = await response.json();
        setData(jsonData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching summary data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Use default values while loading or on error
  const score = data?.chi_score ?? 0;
  const percentage = score / 100.0;
  
  // Scale up when sidebar is closed - use CSS transform for smooth transition
  const scaleFactor = isSidebarOpen ? 1 : 1.25;
  const baseRadius = 100;
  const baseCircleSize = 240;
  const radius = baseRadius;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - percentage);

  const trendValue = Math.abs(data?.chi_trend ?? 0);
  const trendPeriod = data?.trend_period ?? "Last Hour";
  const isPositive = (data?.chi_trend ?? 0) > 0 || data?.trend_direction === "up";
  const trendColor = isPositive ? "#10B981" : "#D62828"; // Green for positive, red for negative
  const trendArrow = isPositive ? "↑" : "↓";

  // Shift down when sidebar is closed
  const trendMarginTop = isSidebarOpen ? "1rem" : "3rem";
  // Increase font size when sidebar is closed
  const trendFontSize = isSidebarOpen ? 16 : 22; // Scale up from 16px to 22px
  const trendArrowSize = isSidebarOpen ? "text-xl" : "text-2xl"; // Scale up arrow size

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="text-[#9CA3AF]">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="text-red-500 text-sm">Error: {error}</div>
      </div>
    );
  }

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
            {score.toFixed(1)}
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
          {trendValue.toFixed(1)} vs {trendPeriod}
        </span>
      </div>
    </div>
  );
}

