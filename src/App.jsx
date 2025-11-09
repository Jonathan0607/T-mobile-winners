import { summaryData, trendData, competitiveData, heatMapData } from './data/mockApi';
import Sidebar from './components/Sidebar';
import VibeScoreCard from './components/VibeScoreCard';
import ActionCard from './components/ActionCard';
import CompetitiveVibeCheck from './components/CompetitiveVibeCheck';
import PredictiveIssueHeatMap from './components/PredictiveIssueHeatMap';

function App() {
  return (
    <div className="flex h-screen bg-gray-900 overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar />
      
      {/* Main Dashboard Area */}
      <div className="flex-1 overflow-y-auto p-6">
        {/* Row 1: Vibe Score Card and Action Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Vibe Score Card - Takes 1 column */}
          <div className="lg:col-span-1">
            <VibeScoreCard
              score={summaryData.chi_score}
              trend={summaryData.trend}
              trendData={trendData}
            />
          </div>
          
          {/* Action Cards - Take 2 columns */}
          <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
            {summaryData.action_cards.map((card) => (
              <ActionCard key={card.id} cardData={card} />
            ))}
          </div>
        </div>
        
        {/* Row 2: Heat Map and Competitive Check */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PredictiveIssueHeatMap heatMapData={heatMapData} />
          <CompetitiveVibeCheck competitiveData={competitiveData} />
        </div>
      </div>
    </div>
  );
}

export default App;