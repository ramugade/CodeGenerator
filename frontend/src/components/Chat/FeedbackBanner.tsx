import { ThumbsUp, ThumbsDown, X } from "lucide-react";
import { useState } from "react";

export const FeedbackBanner = () => {
  const [visible, setVisible] = useState(true);

  if (!visible) return null;

  return (
    <div className="flex items-center justify-center py-4 animate-fade-in">
      <div className="flex items-center gap-4 bg-card border border-border rounded-full px-5 py-2.5 shadow-lg">
        <span className="text-sm text-foreground">Is this conversation helpful so far?</span>
        <div className="flex items-center gap-1">
          <button className="p-2 rounded-full hover:bg-accent transition-colors text-muted-foreground hover:text-foreground">
            <ThumbsUp size={16} />
          </button>
          <button className="p-2 rounded-full hover:bg-accent transition-colors text-muted-foreground hover:text-foreground">
            <ThumbsDown size={16} />
          </button>
        </div>
        <button 
          onClick={() => setVisible(false)}
          className="p-1 rounded-full hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
        >
          <X size={16} />
        </button>
      </div>
    </div>
  );
};
