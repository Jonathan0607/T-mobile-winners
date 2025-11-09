import { useEffect, useRef, useState } from 'react';
import Plot from 'react-plotly.js';
import { HeatmapData, PRESENT_HEATMAP_DATA, PREDICTIVE_HEATMAP_DATA } from '../data/mockData';

interface HeatMapProps {
  isSidebarOpen: boolean;
}

export default function HeatMap({ isSidebarOpen }: HeatMapProps) {
  const [mapView, setMapView] = useState<'Present' | 'Predictive'>('Present');
  const containerRef = useRef<HTMLDivElement>(null);
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [mapHeight, setMapHeight] = useState(450);
  const [mapWidth, setMapWidth] = useState(0);

  const mapData: HeatmapData[] = mapView === 'Present' ? PRESENT_HEATMAP_DATA : PREDICTIVE_HEATMAP_DATA;
  const mapTitle = mapView === 'Present' 
    ? 'Current Issue Distribution' 
    : 'Predicted Issue Distribution (24h Forecast)';

  // Update map dimensions based on container
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current && mapContainerRef.current) {
        // Get the available height minus padding, header, toggle, title, and legend
        const availableHeight = containerRef.current.offsetHeight - 220;
        setMapHeight(Math.max(400, Math.min(550, availableHeight)));
        
        // Get the actual content width (excluding padding)
        const computedStyle = window.getComputedStyle(mapContainerRef.current);
        const paddingLeft = parseFloat(computedStyle.paddingLeft) || 0;
        const paddingRight = parseFloat(computedStyle.paddingRight) || 0;
        const width = mapContainerRef.current.offsetWidth - paddingLeft - paddingRight;
        setMapWidth(Math.max(300, width)); // Minimum width of 300px
      }
    };

    // Initial update with delay to ensure DOM is ready
    const timeoutId = setTimeout(updateDimensions, 100);
    
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    if (mapContainerRef.current) {
      resizeObserver.observe(mapContainerRef.current);
    }
    window.addEventListener('resize', updateDimensions);
    
    return () => {
      clearTimeout(timeoutId);
      resizeObserver.disconnect();
      window.removeEventListener('resize', updateDimensions);
    };
  }, [isSidebarOpen]); // Re-run when sidebar state changes

  // Prepare data for single trace
  const lats = mapData.map((row) => row.lat);
  const lons = mapData.map((row) => row.lon);
  const cities = mapData.map((row) => row.city);
  
  // Determine colors and sizes based on view
  const colors = mapData.map((row) => {
    if (mapView === 'Present') {
      return row.intensity === 'high' ? '#D62828' : row.intensity === 'medium' ? '#FF6B35' : '#E20074';
    } else {
      return row.velocity === 'high' ? '#D62828' : row.velocity === 'medium' ? '#FF6B35' : '#E20074';
    }
  });
  
  const sizes = mapData.map((row) => {
    return row.intensity === 'high' ? 25 : row.intensity === 'medium' ? 18 : 12;
  });

  // Create data trace
  const data = [{
    type: 'scattergeo' as const,
    lat: lats,
    lon: lons,
    mode: 'text+markers' as const,
    text: cities,
    textposition: 'top center' as const,
    textfont: { size: 11, color: 'white' },
    marker: {
      size: sizes,
      color: colors,
      opacity: 0.8,
      line: { width: 2, color: 'white' },
    },
    hovertemplate: '<b>%{text}</b><br>' +
      'Issues: %{customdata[0]}<br>' +
      'Intensity: %{customdata[1]}<br>' +
      'Velocity: %{customdata[2]}' +
      (mapView === 'Predictive' ? '<br><i>Predicted</i>' : '') +
      '<extra></extra>',
    customdata: mapData.map((row) => [
      row.issues,
      row.intensity.charAt(0).toUpperCase() + row.intensity.slice(1),
      row.velocity.charAt(0).toUpperCase() + row.velocity.slice(1)
    ]),
    name: 'Cities',
  }];

  const layout = {
    geo: {
      scope: 'usa',
      projection: {
        type: 'albers usa'
      },
      showland: true,
      landcolor: '#2C2C2C',
      coastlinecolor: '#404040',
      lakecolor: '#1A1A1A',
      showlakes: true,
      showocean: true,
      oceancolor: '#1A1A1A',
      bgcolor: 'rgba(0,0,0,0)',
      lonaxis: { range: [-130, -65] },
      lataxis: { range: [25, 50] },
    },
    margin: { l: 0, r: 0, t: 20, b: 0 },
    height: mapHeight,
    width: mapWidth > 0 ? mapWidth : undefined,
    plot_bgcolor: 'rgba(0,0,0,0)',
    paper_bgcolor: 'rgba(0,0,0,0)',
    showlegend: false,
    font: { color: 'white' },
    autosize: mapWidth === 0, // Use autosize until we have width
  };

  const config = {
    displayModeBar: false,
    responsive: true,
    useResizeHandler: true,
  };

  return (
    <div ref={containerRef} className="bg-[#2C2C2C] rounded-xl p-5 h-full flex flex-col" style={{ position: 'relative', zIndex: 1000, minHeight: '500px', width: '100%' }}>
      <h3 className="text-white text-xl font-semibold mb-3 text-center">Predictive Issue Heat Map</h3>
      
      {/* Map View Toggle */}
      <div className="flex justify-center mb-1">
        <div className="inline-flex rounded-md bg-[#1A1A1A] p-1" style={{ position: 'relative', zIndex: 1001 }}>
          <button
            onClick={() => setMapView('Present')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mapView === 'Present'
                ? 'bg-[#E20074] text-white'
                : 'text-[#CCCCCC] hover:text-white'
            }`}
          >
            Present
          </button>
          <button
            onClick={() => setMapView('Predictive')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mapView === 'Predictive'
                ? 'bg-[#E20074] text-white'
                : 'text-[#CCCCCC] hover:text-white'
            }`}
          >
            Predictive
          </button>
        </div>
      </div>

      {/* Map - Fill available space with high z-index */}
      <div 
        ref={mapContainerRef}
        className="rounded-xl overflow-visible bg-[#2C2C2C] flex-1 flex items-center justify-center" 
        style={{ position: 'relative', zIndex: 1002, minHeight: `${mapHeight}px`, width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}
      >
        <div style={{ position: 'relative', zIndex: 1003, width: '100%', height: '100%' }}>
          {mapWidth > 0 && (
            <Plot 
              data={data} 
              layout={layout} 
              config={config} 
              style={{ width: '100%', height: `${mapHeight}px`, position: 'relative', zIndex: 1004, maxWidth: '100%' }} 
              useResizeHandler={true}
            />
          )}
        </div>
      </div>

      {/* Map Title */}
      <p className="text-xs text-[#9CA3AF] mt-3 mb-4 italic text-center">{mapTitle}</p>

      {/* Legend */}
      <div className="flex gap-6 mt-4 text-sm justify-center flex-wrap">
        {mapView === 'Present' ? (
          <>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#D62828] rounded-full"></div>
              <span className="text-[#D1D5DB]">High Intensity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#FF6B35] rounded-full"></div>
              <span className="text-[#D1D5DB]">Medium Intensity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#E20074] rounded-full"></div>
              <span className="text-[#D1D5DB]">Low Intensity</span>
            </div>
          </>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#D62828] rounded-full"></div>
              <span className="text-[#D1D5DB]">High Velocity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#FF6B35] rounded-full"></div>
              <span className="text-[#D1D5DB]">Medium Velocity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#E20074] rounded-full"></div>
              <span className="text-[#D1D5DB]">Low Velocity</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

