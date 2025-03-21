import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ApiClientRest } from '../rest/api_client_rest';
import Chat from './Chat';
import WelcomeScreen from './WelcomeScreen';
import ChatSidebar from './ChatSidebar';
import { setActiveChat } from '../services/chatStorage';

const ChatView: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const [activeChatId, setActiveChatId] = useState<string | null>(chatId || null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const apiClient = useMemo(() => new ApiClientRest(), []);
  const navigate = useNavigate();

  // Check active chat from storage on mount
  useEffect(() => {
    // If URL has chatId, use it
    if (chatId) {
      setActiveChatId(chatId);
      setActiveChat(chatId);
    } else {
      // No active chat in URL - show welcome screen
      setActiveChatId(null);
    }
  }, [chatId]);

  const handleSelectChat = (selectedChatId: string) => {
    setActiveChatId(selectedChatId);
    navigate(`/chat/${selectedChatId}`);
  };

  const handleNewChat = () => {
    // Clear active chat and go to welcome screen
    setActiveChat(null);
    setActiveChatId(null);
    navigate('/');
  };

  const handleChatCreated = (newChatId: string) => {
    setActiveChatId(newChatId);
    navigate(`/chat/${newChatId}`);
  };

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Mobile sidebar toggle */}
      <div className="lg:hidden fixed bottom-4 right-4 z-10">
        <button
          className="btn btn-circle btn-primary"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          {sidebarOpen ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        transition-transform duration-300 ease-in-out
        lg:translate-x-0 lg:relative lg:flex
        fixed top-0 bottom-0 left-0 z-20 lg:z-0
        h-full
      `}>
        <ChatSidebar
          activeChatId={activeChatId}
          onSelectChat={handleSelectChat}
          onNewChat={handleNewChat}
        />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {activeChatId ? (
          <Chat chatId={activeChatId} client={apiClient} />
        ) : (
          <WelcomeScreen onChatCreated={handleChatCreated} />
        )}
      </div>
    </div>
  );
};

export default ChatView;
