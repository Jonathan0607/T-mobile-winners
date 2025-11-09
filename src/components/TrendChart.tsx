import { useEffect, useRef, useState } from 'react';
import Plot from 'react-plotly.js';

interface TrendDataPoint {
  time: string | Date;
  score: number;
}

export default function TrendChart() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [chartHeight, setChartHeight] = useState(400);
  const [chartWidth, setChartWidth] = useState(0);
  const [trendData, setTrendData] = useState<TrendDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch trend data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5001/api/vibecheck/summary');
        if (!response.ok) {
          throw new Error('Failed to fetch summary data');
        }
        const jsonData = await response.json();
        if (jsonData.trend_data && Array.isArray(jsonData.trend_data)) {
          // Remove the last data point
          const trendDataWithoutLast = jsonData.trend_data.slice(0, -1);
          setTrendData(trendDataWithoutLast);
          console.log(trendDataWithoutLast);
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching trend data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Update chart dimensions based on container
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        // Get the actual content width (excluding padding)
        const computedStyle = window.getComputedStyle(containerRef.current);
        const paddingLeft = parseFloat(computedStyle.paddingLeft) || 0;
        const paddingRight = parseFloat(computedStyle.paddingRight) || 0;
        const width = containerRef.current.offsetWidth - paddingLeft - paddingRight;
        setChartWidth(width);
        // Calculate height based on width for responsive design
        // Wider containers get proportionally taller charts
        setChartHeight(Math.max(350, Math.min(500, width * 0.25)));
      }
    };

    // Initial update with slight delay to ensure DOM is ready
    const timeoutId = setTimeout(updateDimensions, 0);
    
    // Use ResizeObserver for better performance
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    
    // Also listen to window resize as fallback
    window.addEventListener('resize', updateDimensions);
    
    return () => {
      clearTimeout(timeoutId);
      resizeObserver.disconnect();
      window.removeEventListener('resize', updateDimensions);
    };
  }, []);

  // Format time for x-axis - handle both string and Date objects
  const formatTime = (time: string | Date) => {
    if (typeof time === 'string') {
      // If it's already formatted as "HH:MM", return as is
      if (time.includes(':') && !time.includes('-')) {
        return time;
      }
      // Otherwise try to parse it
      const d = new Date(time);
      if (isNaN(d.getTime())) {
        return time; // Return original if not a valid date
      }
      const hours = d.getHours();
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const displayHour = hours % 12 || 12;
      return `${displayHour} ${ampm}`;
    } else {
      const d = new Date(time);
      const hours = d.getHours();
      const ampm = hours >= 12 ? 'PM' : 'AM';
      const displayHour = hours % 12 || 12;
      return `${displayHour} ${ampm}`;
    }
  };

  // Prepare data for Plotly line chart
  const plotlyData = trendData.length > 0 ? [
    {
      x: trendData.map((d) => formatTime(d.time)),
      y: trendData.map((d) => d.score),
      type: 'scatter' as const,
      mode: 'lines+markers' as const,
      line: { color: '#E20074', width: 3 },
      marker: { size: 6, color: '#E20074' },
      fill: 'tozeroy' as const,
      fillcolor: 'rgba(226, 0, 116, 0.1)',
      hovertemplate: '<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>',
      name: 'CHI Score',
    },
  ] : [];

  const plotlyLayout = {
    plot_bgcolor: '#2C2C2C',
    paper_bgcolor: '#2C2C2C',
    font: { color: '#FFFFFF', size: 12, family: 'Arial, sans-serif' },
    margin: { l: 60, r: 60, t: 30, b: 80 },
    height: chartHeight,
    width: chartWidth > 0 ? chartWidth : undefined,
    autosize: chartWidth === 0, 
    xaxis: {
      title: {
        text: 'Time (Last 24 Hours)',
        font: { color: '#FFFFFF', size: 14, family: 'Arial, sans-serif' },
      },
      gridcolor: '#404040',
      showgrid: true,
      tickfont: { size: 10, color: '#9CA3AF' },
      linecolor: '#555555',
      linewidth: 1,
      tickangle: -45,
      nticks: 12,
    },
    yaxis: {
      title: {
        text: 'CHI Score',
        font: { color: '#FFFFFF', size: 14, family: 'Arial, sans-serif' },
      },
      gridcolor: '#404040',
      showgrid: true,
      range: trendData.length > 0 ? [
        Math.max(0, Math.min(...trendData.map(d => d.score)) - 10),
        Math.min(100, Math.max(...trendData.map(d => d.score)) + 10)
      ] : [0, 100],
      tickfont: { size: 11, color: '#9CA3AF' },
      linecolor: '#555555',
      linewidth: 1,
    },
    showlegend: false,
    hovermode: 'closest' as const,
  };

  const plotlyConfig = {
    displayModeBar: false,
    responsive: true,
    useResizeHandler: true,
  };

  if (loading) {
    return (
      <div className="bg-[#2C2C2C] rounded-xl p-6 w-full overflow-hidden" ref={containerRef} style={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <h3 className="text-white text-xl font-semibold mb-4 text-center">
          24-Hour CHI Score Trend
        </h3>
        <div className="text-[#9CA3AF] text-center py-8">Loading trend data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-[#2C2C2C] rounded-xl p-6 w-full overflow-hidden" ref={containerRef} style={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <h3 className="text-white text-xl font-semibold mb-4 text-center">
          24-Hour CHI Score Trend
        </h3>
        <div className="text-red-500 text-sm text-center py-8">Error: {error}</div>
      </div>
    );
  }

  if (trendData.length === 0) {
    return (
      <div className="bg-[#2C2C2C] rounded-xl p-6 w-full overflow-hidden" ref={containerRef} style={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <h3 className="text-white text-xl font-semibold mb-4 text-center">
          24-Hour CHI Score Trend
        </h3>
        <div className="text-[#9CA3AF] text-center py-8">No trend data available.</div>
      </div>
    );
  }

  return (
    <div className="bg-[#2C2C2C] rounded-xl p-6 w-full overflow-hidden" ref={containerRef} style={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
      <h3 className="text-white text-xl font-semibold mb-4 text-center">
        24-Hour CHI Score Trend
      </h3>
      <div className="w-full overflow-hidden" style={{ width: '100%', height: `${chartHeight}px`, maxWidth: '100%', boxSizing: 'border-box' }}>
        <Plot 
          data={plotlyData} 
          layout={plotlyLayout} 
          config={plotlyConfig}
          style={{ width: '100%', height: '100%', maxWidth: '100%' }}
          useResizeHandler={true}
        />
      </div>
    </div>
  );
}

