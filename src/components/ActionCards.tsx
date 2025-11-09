import { useEffect, useState } from 'react';

interface ActionCard {
  id: string;
  title: string;
  insight: string;
  priority: string;
  team: string;
  color: string;
}

export default function ActionCards() {
  const [actionCards, setActionCards] = useState<ActionCard[]>([]);
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
        setActionCards(jsonData.action_cards || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
        console.error('Error fetching action cards:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-3">
        <div className="text-[#9CA3AF] text-center py-4">Loading action cards...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-3">
        <div className="text-red-500 text-sm text-center py-4">Error: {error}</div>
      </div>
    );
  }

  if (actionCards.length === 0) {
    return (
      <div className="space-y-3">
        <div className="text-[#9CA3AF] text-center py-4">No action items at this time.</div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {actionCards.map((action: ActionCard) => (
        <div
          key={action.id}
          className="bg-[#2C2C2C] rounded-xl p-3 border-l-4 shadow-lg"
          style={{ borderLeftColor: action.color }}
        >
          <div className="flex justify-between items-start">
            <div className="flex-1">
              <div
                className="font-bold text-xs uppercase mb-2"
                style={{ color: action.color }}
              >
                {action.priority} • {action.team}
              </div>
              <h4 className="text-white text-base mb-2">{action.title}</h4>
              <p className="text-[#CCCCCC] text-sm mb-2">{action.insight}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

