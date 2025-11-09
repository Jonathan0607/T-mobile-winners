import VibeScoreCard from '../components/VibeScoreCard';
import ActionCards from '../components/ActionCards';
import HeatMap from '../components/HeatMap';
import CompetitiveChart from '../components/CompetitiveChart';
import TrendChart from '../components/TrendChart';

interface HomeProps {
  isSidebarOpen: boolean;
}

export default function Home({ isSidebarOpen }: HomeProps) {
  return (
    <>
      {/* Header and Metrics Section */}
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-8 ml-8">Vibe Check Dashboard</h1>

        {/* Row 1: Critical Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Vibe Score Card */}
          <div className="lg:col-span-1">
            <VibeScoreCard isSidebarOpen={isSidebarOpen} />
          </div>

          {/* Action Cards */}
          <div className="lg:col-span-2">
            <ActionCards />
          </div>
        </div>
      </div>

      {/* Row 2: Full-Width Trend Chart */}
      <div 
        className="mb-8"
        style={!isSidebarOpen ? {
          width: '100vw',
          marginLeft: 'calc(50% - 50vw)',
          paddingLeft: '2rem',
          paddingRight: '2rem',
          boxSizing: 'border-box'
        } : {
          paddingLeft: '2rem',
          paddingRight: '2rem',
          width: '100%'
        }}
      >
        <TrendChart />
      </div>

      {/* Row 3: Insights */}
      <div className="px-8 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
          {/* Predictive Heat Map */}
          <div className="w-full">
            <HeatMap isSidebarOpen={isSidebarOpen} />
          </div>

          {/* Competitive Chart */}
          <div className="w-full">
            <CompetitiveChart isSidebarOpen={isSidebarOpen} />
          </div>
        </div>
      </div>
    </>
  );
}

