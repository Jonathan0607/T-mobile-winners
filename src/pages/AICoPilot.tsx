import { useEffect, useState, useRef } from 'react';

interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export default function AICoPilot() {
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory, isLoading]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      sender: 'user',
      text: inputText.trim(),
      timestamp: new Date(),
    };

    // Add user message to chat history
    setChatHistory((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5001/api/vibecheck/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userMessage.text }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const aiMessage: ChatMessage = {
        sender: 'ai',
        text: data.response || 'I apologize, but I could not generate a response.',
        timestamp: new Date(),
      };

      setChatHistory((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'An error occurred';
      
      setError(`Error: ${errorMessage}`);
      
      // Add error message to chat
      const errorMessageObj: ChatMessage = {
        sender: 'ai',
        text: 'Sorry, I encountered an error while processing your request. Please make sure the Flask server is running.',
        timestamp: new Date(),
      };
      setChatHistory((prev) => [...prev, errorMessageObj]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-screen bg-[#1A1A1A] text-white" style={{ height: '100vh', overflow: 'hidden' }}>
      {/* Header */}
      <div className="bg-[#2C2C2C] border-b border-[#555555] p-6 flex-shrink-0">
        <h1 className="text-3xl font-bold ml-8">AI Co-Pilot</h1>
        <p className="text-[#9CA3AF] mt-2 ml-8">Ask Nemotron AI for insights about your vibe check data</p>
      </div>

      {/* Chat History Window */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 min-h-0">
        {chatHistory.length === 0 && !isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-[#9CA3AF]">
              <p className="text-xl mb-2">👋 Welcome to AI Co-Pilot</p>
              <p className="text-sm">Start a conversation by asking a question below</p>
            </div>
          </div>
        )}

        {chatHistory.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg p-4 ${
                message.sender === 'user'
                  ? 'bg-[#3C3C3C] text-white'
                  : 'bg-[#2C2C2C] border-2 border-[#E20074] text-white'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`text-sm font-semibold ${
                    message.sender === 'user' ? 'text-[#CCCCCC]' : 'text-[#E20074]'
                  }`}
                >
                  {message.sender === 'user' ? 'You' : 'Nemotron AI'}
                </span>
                <span className="text-xs text-[#9CA3AF] ml-4">
                  {formatTime(message.timestamp)}
                </span>
              </div>
              <p className="whitespace-pre-wrap">{message.text}</p>
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[#2C2C2C] border-2 border-[#E20074] rounded-lg p-4 max-w-3xl">
              <div className="flex items-center space-x-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-[#E20074] rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-[#E20074] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-[#E20074] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-[#9CA3AF] text-sm">Nemotron is thinking...</span>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 text-red-400 text-sm">
            {error}
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="bg-[#2C2C2C] border-t border-[#555555] p-4 flex-shrink-0">
        <div className="flex gap-4 max-w-5xl mx-auto">
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask Nemotron AI a question..."
            disabled={isLoading}
            className="flex-1 bg-[#1A1A1A] border border-[#555555] rounded-lg px-4 py-3 text-white placeholder-[#9CA3AF] focus:outline-none focus:border-[#E20074] disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
            className="bg-[#E20074] hover:bg-[#C1005A] disabled:bg-[#555555] disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-[#E20074] focus:ring-offset-2 focus:ring-offset-[#2C2C2C]"
          >
            Ask Nemotron
          </button>
        </div>
      </div>
    </div>
  );
}

