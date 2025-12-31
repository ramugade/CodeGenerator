import { useEffect } from 'react';
import { useChatStore } from '../../store/chatStore';
import { sessionAPI } from '../../services/api';

export const Sidebar = () => {
  const { sessions, currentSessionId, setCurrentSession, setSessions, deleteSession } = useChatStore();

  useEffect(() => {
    sessionAPI.listSessions().then(data => setSessions(data.sessions));
  }, [setSessions]);

  const handleNewChat = () => {
    // Backend will create session on first query
    setCurrentSession(null);
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this session?')) {
      await sessionAPI.deleteSession(sessionId);
      deleteSession(sessionId);
    }
  };

  return (
    <div className="w-72 bg-gray-100 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 flex flex-col h-full">
      <div className="p-5 border-b border-gray-200 dark:border-gray-800">
        <button
          onClick={handleNewChat}
          className="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600
                     hover:from-blue-700 hover:to-purple-700 text-white rounded-lg
                     font-semibold shadow-sm transition-all duration-200
                     hover:shadow-md flex items-center justify-center gap-2"
        >
          <span className="text-lg">+</span>
          <span>New Chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {sessions.length === 0 ? (
          <div className="p-6 text-center text-gray-400 dark:text-gray-600 text-sm">
            No chat history yet
          </div>
        ) : (
          sessions.map(session => (
            <div
              key={session.id}
              onClick={() => setCurrentSession(session.id)}
              className={`p-4 border-b border-gray-200 dark:border-gray-800 cursor-pointer
                         transition-all duration-150 ${
                currentSessionId === session.id
                  ? 'bg-blue-50 dark:bg-gray-800 border-l-4 border-l-blue-500'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate mb-1.5">
                    {session.title}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    {new Date(session.created_at).toLocaleDateString()}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400 mt-1.5 font-mono">
                    ${session.total_cost_usd.toFixed(4)} • {session.total_tokens.toLocaleString()} tokens
                  </div>
                </div>

                <button
                  onClick={(e) => handleDeleteSession(session.id, e)}
                  className="ml-2 text-gray-400 dark:text-gray-500 hover:text-red-500
                           dark:hover:text-red-400 transition-colors text-xl leading-none"
                  title="Delete session"
                >
                  ×
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
