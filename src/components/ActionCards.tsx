import { ActionCard } from '../data/mockData';
import { MOCK_SUMMARY } from '../data/mockData';

export default function ActionCards() {
  return (
    <div className="space-y-3">
      {MOCK_SUMMARY.action_cards.map((action: ActionCard) => (
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

