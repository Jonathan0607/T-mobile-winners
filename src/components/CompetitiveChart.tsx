import { useEffect, useRef, useState } from 'react';
import Plot from 'react-plotly.js';

interface CompetitiveChartProps {
  isSidebarOpen: boolean;
}

interface CompetitiveSummary {
  carrier: string;
  score: number;
  color: string;
}

export default function CompetitiveChart({ isSidebarOpen }: CompetitiveChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [chartHeight, setChartHeight] = useState(350);
  const [chartWidth, setChartWidth] = useState(0);
  const [competitiveData, setCompetitiveData] = useState<CompetitiveSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch competitive data from API
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5001/api/vibecheck/summary');
        if (!response.ok) {
          throw new Error('Failed to fetch summary data');
        }
        const jsonData = await response.json();
        if (jsonData.competitive_summary && Array.isArray(jsonData.competitive_summary)) {
          setCompetitiveData(jsonData.competitive_summary);
        }
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching competitive data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Update chart dimensions based on container
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current && chartContainerRef.current) {
        // Get the available height minus padding and header
        const availableHeight = containerRef.current.offsetHeight - 180; // Account for header, padding, insight
        setChartHeight(Math.max(280, Math.min(380, availableHeight * 0.85))); // 85% of available height, max 380px
        
        // Get the actual content width of the chart container (excluding its padding)
        const chartComputedStyle = window.getComputedStyle(chartContainerRef.current);
        const chartPaddingLeft = parseFloat(chartComputedStyle.paddingLeft) || 10;
        const chartPaddingRight = parseFloat(chartComputedStyle.paddingRight) || 10;
        const width = chartContainerRef.current.offsetWidth - chartPaddingLeft - chartPaddingRight;
        setChartWidth(Math.max(200, width)); // Minimum width of 200px
      }
    };

    // Initial update with delay to ensure DOM is ready
    const timeoutId = setTimeout(updateDimensions, 100);
    
    // Use ResizeObserver for better performance
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    if (chartContainerRef.current) {
      resizeObserver.observe(chartContainerRef.current);
    }
    
    // Also listen to window resize as fallback
    window.addEventListener('resize', updateDimensions);
    
    return () => {
      clearTimeout(timeoutId);
      resizeObserver.disconnect();
      window.removeEventListener('resize', updateDimensions);
    };
  }, [isSidebarOpen, competitiveData]); // Re-run when sidebar state or data changes

  const carriers = competitiveData.map((d) => d.carrier);
  const scores = competitiveData.map((d) => d.score);
  const colors = competitiveData.map((d) => d.color || (d.carrier.includes('T-Mobile') ? '#E20074' : '#666666'));

  const plotlyData = competitiveData.length > 0 ? [
    {
      x: carriers,
      y: scores,
      type: 'bar' as const,
      marker: {
        color: colors,
        line: { width: 0 },
      },
      text: scores.map(s => s.toFixed(1)),
      textposition: 'outside' as const,
      textfont: { color: 'white', size: 12 },
      hovertemplate: '<b>%{x}</b><br>Score: %{y}<extra></extra>',
    },
  ] : [];

  const layout = {
    plot_bgcolor: '#2C2C2C',
    paper_bgcolor: '#2C2C2C',
    font: { color: 'white', family: 'Arial, sans-serif' },
    height: chartHeight,
    width: chartWidth > 0 ? chartWidth : undefined,
    margin: { l: 50, r: 40, t: 20, b: 80 }, // Increased right and bottom margins for text labels
    xaxis: { 
      showgrid: false, 
      showline: true,
      linecolor: '#555555',
      tickfont: { color: 'white', size: 11 },
      title: { text: 'Carrier', font: { color: 'white', size: 14 } },
    },
    yaxis: { 
      showgrid: true, 
      gridcolor: '#404040',
      showline: true,
      linecolor: '#555555',
      range: competitiveData.length > 0 ? [
        Math.max(0, Math.min(...scores) - 5),
        Math.min(100, Math.max(...scores) + 5)
      ] : [0, 100],
      tickfont: { color: 'white', size: 11 },
      title: { text: 'Vibe Score', font: { color: 'white', size: 14 } },
    },
    showlegend: false,
    autosize: chartWidth === 0, // Use autosize until we have width
  };

  const config = {
    displayModeBar: false,
    responsive: true,
    useResizeHandler: true,
  };

  if (loading) {
    return (
      <div ref={containerRef} className="bg-[#2C2C2C] rounded-xl p-5 h-full flex flex-col" style={{ minHeight: '450px', width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <h3 className="text-white text-xl font-semibold mb-4 text-center">Competition Vibe Check</h3>
        <div className="text-[#9CA3AF] text-center py-8">Loading competitive data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div ref={containerRef} className="bg-[#2C2C2C] rounded-xl p-5 h-full flex flex-col" style={{ minHeight: '450px', width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <h3 className="text-white text-xl font-semibold mb-4 text-center">Competition Vibe Check</h3>
        <div className="text-red-500 text-sm text-center py-8">Error: {error}</div>
      </div>
    );
  }

  if (competitiveData.length === 0) {
    return (
      <div ref={containerRef} className="bg-[#2C2C2C] rounded-xl p-5 h-full flex flex-col" style={{ minHeight: '450px', width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
        <h3 className="text-white text-xl font-semibold mb-4 text-center">Competition Vibe Check</h3>
        <div className="text-[#9CA3AF] text-center py-8">No competitive data available.</div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="bg-[#2C2C2C] rounded-xl p-5 h-full flex flex-col" style={{ minHeight: '450px', width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
      <h3 className="text-white text-xl font-semibold mb-4 text-center">Competition Vibe Check</h3>
      
      {/* Bar Chart */}
      <div 
        ref={chartContainerRef}
        className="rounded-xl bg-[#2C2C2C] flex items-center justify-center" 
        style={{ 
          height: `${chartHeight + 40}px`, // Extra height for text labels
          flexShrink: 0, 
          width: '100%', 
          maxWidth: '100%', 
          boxSizing: 'border-box',
          overflow: 'visible',
          padding: '10px'
        }}
      >
        {chartWidth > 0 && (
          <div style={{ width: '100%', height: '100%', overflow: 'visible' }}>
            <Plot 
              data={plotlyData} 
              layout={layout} 
              config={config} 
              style={{ width: '100%', height: `${chartHeight}px`, maxWidth: '100%' }}
              useResizeHandler={true}
            />
          </div>
        )}
      </div>
    </div>
  );
}

