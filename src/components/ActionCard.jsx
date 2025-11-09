const ActionCard = ({ cardData }) => {
  const getBorderColor = () => {
    if (cardData.priority === 'Critical') {
      return 'border-red-500';
    } else if (cardData.priority === 'High') {
      return 'border-yellow-500';
    }
    return 'border-gray-600';
  };

  const getPriorityColor = () => {
    if (cardData.priority === 'Critical') {
      return 'text-red-500';
    } else if (cardData.priority === 'High') {
      return 'text-yellow-500';
    }
    return 'text-gray-400';
  };

  return (
    <div className={`bg-gray-800 rounded-lg p-6 border-2 ${getBorderColor()} flex flex-col justify-between h-full`}>
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className={`text-xs font-semibold uppercase ${getPriorityColor()}`}>
            {cardData.priority}
          </span>
          <span className="text-xs text-gray-400">{cardData.location}</span>
        </div>
        
        <h3 className="text-xl font-bold text-white mb-2">{cardData.title}</h3>
        
        <div className="mb-2">
          <span className="text-sm text-gray-400">Team: </span>
          <span className="text-sm text-white font-semibold">{cardData.team}</span>
        </div>
        
        <p className="text-sm text-gray-300 mb-4">{cardData.insight}</p>
      </div>
      
      <div className="flex justify-end mt-4">
        <button className="bg-magenta hover:bg-magenta/90 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors">
          Take Action
        </button>
      </div>
    </div>
  );
};

export default ActionCard;
