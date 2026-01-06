import { LucideIcon } from "lucide-react";

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  badge?: string;
  active?: boolean;
  onClick?: () => void;
}

export const SidebarItem = ({ icon: Icon, label, badge, active, onClick }: SidebarItemProps) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
      active 
        ? "bg-sidebar-accent text-sidebar-accent-foreground" 
        : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
    }`}
  >
    <Icon size={18} />
    <span className="flex-1 text-left truncate">{label}</span>
    {badge && (
      <span className="px-1.5 py-0.5 text-xs bg-primary/20 text-primary rounded-md font-medium">
        {badge}
      </span>
    )}
  </button>
);
