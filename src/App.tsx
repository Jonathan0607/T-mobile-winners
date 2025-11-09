import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import CompetitiveAnalysis from './pages/CompetitiveIntelligence';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentPage, setCurrentPage] = useState<'home' | 'competitive'>('home');

  return (
    <div className="min-h-screen bg-[#1A1A1A] text-white">
      <Sidebar 
        isOpen={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
      />
      
      {/* Main Content */}
      <main
        className={`min-h-screen transition-all duration-300 ease-in-out ${
          sidebarOpen ? 'ml-[21rem]' : 'ml-0'
        }`}
        style={{ 
          width: sidebarOpen ? 'calc(100% - 21rem)' : '100%',
          flexShrink: 0
        }}
      >
        <div className="w-full h-full">
          {currentPage === 'home' ? (
            <Home isSidebarOpen={sidebarOpen} />
          ) : (
            <CompetitiveAnalysis />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;

