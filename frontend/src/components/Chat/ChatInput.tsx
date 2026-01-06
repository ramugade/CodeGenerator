import { useState } from "react";
import { CornerDownLeft } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
}

export const ChatInput = ({ onSend }: ChatInputProps) => {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSend(message);
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-border/50 bg-background">
      <div className="max-w-3xl mx-auto px-4 py-4">
        <form onSubmit={handleSubmit}>
          <div className="relative bg-secondary rounded-2xl border border-border/50 focus-within:border-muted-foreground/30 transition-colors">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything"
              className="w-full bg-transparent px-5 py-4 pr-14 text-foreground placeholder:text-muted-foreground focus:outline-none"
            />
            
            {/* Send button */}
            <button
              type="submit"
              disabled={!message.trim()}
              className={`absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-xl transition-all duration-200 ${
                message.trim()
                  ? "bg-foreground text-background hover:bg-foreground/90"
                  : "bg-muted text-muted-foreground cursor-not-allowed"
              }`}
            >
              <CornerDownLeft size={18} />
            </button>
          </div>
        </form>
        
        {/* Disclaimer */}
        <p className="text-center text-xs text-muted-foreground mt-3">
          ChatGPT can make mistakes. Check important info.{" "}
          <a href="#" className="underline hover:text-foreground transition-colors">
            See Cookie Preferences
          </a>
          .
        </p>
      </div>
    </div>
  );
};
