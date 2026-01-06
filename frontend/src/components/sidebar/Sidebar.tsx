import { useEffect, useMemo } from "react";
import {
  PenSquare,
  Search,
  MessageSquare,
  MoreHorizontal,
  User
} from "lucide-react";
import { sessionAPI } from "../../services/api";
import { useChatStore } from "../../store/chatStore";
import type { SSEEventData } from "../../types/events";

const groupLabelForDate = (iso: string) => {
  const date = new Date(iso);
  const today = new Date();
  const diffMs = today.setHours(0, 0, 0, 0) - date.setHours(0, 0, 0, 0);
  const diffDays = diffMs / (1000 * 60 * 60 * 24);

  if (diffDays <= 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays <= 7) return "Previous 7 Days";
  return "Older";
};

export const Sidebar = () => {
  const {
    sessions,
    currentSessionId,
    setSessions,
    setCurrentSession,
    deleteSession: deleteSessionFromStore,
    clearEvents,
    setEvents,
    updateCurrentCost,
    setIsComplete,
    setError,
    setLastUserQuery,
  } = useChatStore();

  useEffect(() => {
    // Fetch sessions from backend
    sessionAPI.listSessions()
      .then((data) => {
        const formattedSessions = (data.sessions || []).map((s: any) => ({
          id: s.session_id,
          title: s.title,
          created_at: s.created_at,
          updated_at: s.updated_at,
          total_tokens: s.total_tokens || 0,
          total_cost_usd: s.total_cost_usd || 0
        }));
        setSessions(formattedSessions);
      })
      .catch((error) => console.error("Failed to load sessions:", error));
  }, [setSessions]);

  const handleNewChat = () => {
    setCurrentSession(null);
    clearEvents();
    setLastUserQuery(null);
  };

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm("Delete this session?")) {
      try {
        await sessionAPI.deleteSession(sessionId);
        deleteSessionFromStore(sessionId);
      } catch (error) {
        console.error("Failed to delete session:", error);
      }
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    if (sessionId === currentSessionId) return;
    try {
      const data = await sessionAPI.getSession(sessionId);
      const messages = Array.isArray(data.messages) ? data.messages : [];
      const ordered = [...messages].sort((a, b) => a.order - b.order);
      const loadedEvents = ordered.map((msg: any) => ({
        type: msg.type,
        data: msg.content,
      })) as SSEEventData[];

      setCurrentSession(sessionId);
      setEvents(loadedEvents);
      updateCurrentCost(data.total_tokens || 0, data.total_cost_usd || 0);
      setIsComplete(loadedEvents.some((event) => event.type === "complete"));
      setError(null);
      setLastUserQuery(null);
    } catch (error) {
      console.error("Failed to load session:", error);
    }
  };

  const sortedSessions = useMemo(() => {
    return [...sessions].sort((a, b) => {
      const aTime = new Date(a.updated_at ?? a.created_at).getTime();
      const bTime = new Date(b.updated_at ?? b.created_at).getTime();
      return bTime - aTime;
    });
  }, [sessions]);

  const groupedSessions = useMemo(() => {
    return sortedSessions.reduce<Record<string, typeof sessions>>((acc, session) => {
      const label = groupLabelForDate(session.updated_at ?? session.created_at);
      if (!acc[label]) acc[label] = [];
      acc[label].push(session);
      return acc;
    }, {});
  }, [sortedSessions]);

  return (
    <aside className="w-64 h-screen bg-sidebar border-r border-sidebar-border flex flex-col">
      {/* Header */}
      <div className="p-3 flex items-center justify-between">
        <button className="p-2 rounded-lg hover:bg-sidebar-accent transition-colors">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-sidebar-foreground">
            <path d="M3 12h18M3 6h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </button>
        <button
          onClick={handleNewChat}
          className="p-2 rounded-lg hover:bg-sidebar-accent transition-colors text-sidebar-foreground"
        >
          <PenSquare size={20} />
        </button>
      </div>

      {/* Search */}
      <div className="px-3 mb-2">
        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-sidebar-foreground hover:bg-sidebar-accent/50 transition-colors">
          <Search size={18} />
          <span>Search chats</span>
        </button>
      </div>

      {/* Chat history */}
      <div className="flex-1 overflow-y-auto px-2 scrollbar-thin">
        {sessions.length === 0 ? (
          <div className="p-6 text-center text-sm text-sidebar-foreground/50">
            No chat history yet
          </div>
        ) : (
          Object.entries(groupedSessions).map(([label, group]) => (
            <div key={label} className="mt-4 first:mt-0">
              <h3 className="px-3 mb-2 text-xs font-medium text-sidebar-foreground/50">
                {label}
              </h3>
              <div className="space-y-0.5">
                {group.map((session) => (
                  <div
                    key={session.id}
                    className={`group w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-sidebar-foreground hover:bg-sidebar-accent transition-colors cursor-pointer ${
                      currentSessionId === session.id
                        ? "bg-sidebar-accent"
                        : ""
                    }`}
                  >
                    <MessageSquare size={16} className="shrink-0 opacity-60" />
                    <span
                      className="flex-1 text-left truncate"
                      onClick={() => handleSelectSession(session.id)}
                    >
                      {session.title}
                    </span>
                    <button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      className="shrink-0 opacity-0 group-hover:opacity-60 transition-opacity"
                      aria-label="Delete session"
                    >
                      <MoreHorizontal size={16} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {/* User section at bottom */}
      <div className="border-t border-sidebar-border p-3">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-sidebar-accent transition-colors cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
            <User size={16} className="text-primary-foreground" />
          </div>
          <span className="text-sm font-medium text-sidebar-foreground">Subodh Ramugade</span>
        </div>
      </div>

    </aside>
  );
};
