import { useEffect, useRef, useState } from 'react';
import Plot from 'react-plotly.js';
import { generateTrendData } from '../data/mockData';

export default function TrendChart() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [chartHeight, setChartHeight] = useState(400);
  const [chartWidth, setChartWidth] = useState(0);

  // Generate trend data
  const trendData = generateTrendData();

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

  // Format time for x-axis - show hours only for cleaner display
  const formatTime = (date: Date) => {
    const d = new Date(date);
    const hours = d.getHours();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHour = hours % 12 || 12;
    return `${displayHour} ${ampm}`;
  };

  // Prepare data for Plotly line chart
  const plotlyData = [
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
  ];

  const plotlyLayout = {
    plot_bgcolor: '#2C2C2C',
    paper_bgcolor: '#2C2C2C',
    font: { color: '#FFFFFF', size: 12, family: 'Arial, sans-serif' },
    margin: { l: 60, r: 60, t: 30, b: 80 },
    height: chartHeight,
    width: chartWidth > 0 ? chartWidth : undefined,
    autosize: chartWidth === 0, // Use autosize until we have width
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
      range: [75, 95],
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

