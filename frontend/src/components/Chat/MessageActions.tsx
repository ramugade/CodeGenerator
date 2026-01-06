import { Copy, ThumbsUp, ThumbsDown, Upload, RefreshCw, MoreHorizontal } from "lucide-react";
import { useState } from "react";

interface MessageActionsProps {
  onRegenerate?: () => void;
}

export const MessageActions = ({ onRegenerate }: MessageActionsProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex items-center gap-1 mt-3 animate-fade-in">
      <ActionButton icon={<Copy size={16} />} onClick={handleCopy} active={copied} />
      <ActionButton icon={<ThumbsUp size={16} />} />
      <ActionButton icon={<ThumbsDown size={16} />} />
      <ActionButton icon={<Upload size={16} />} />
      <ActionButton icon={<RefreshCw size={16} />} onClick={onRegenerate} />
      <ActionButton icon={<MoreHorizontal size={16} />} />
    </div>
  );
};

interface ActionButtonProps {
  icon: React.ReactNode;
  onClick?: () => void;
  active?: boolean;
}

const ActionButton = ({ icon, onClick, active }: ActionButtonProps) => (
  <button
    onClick={onClick}
    className={`p-2 rounded-lg transition-all duration-200 hover:bg-accent ${
      active ? "text-primary" : "text-muted-foreground hover:text-foreground"
    }`}
  >
    {icon}
  </button>
);
