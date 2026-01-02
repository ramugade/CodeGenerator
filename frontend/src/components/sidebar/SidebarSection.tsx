interface SidebarSectionProps {
  title: string;
  children: React.ReactNode;
}

export const SidebarSection = ({ title, children }: SidebarSectionProps) => (
  <div className="mt-6">
    <h3 className="px-3 mb-2 text-xs font-medium text-sidebar-foreground/60 uppercase tracking-wider">
      {title}
    </h3>
    <div className="space-y-0.5">{children}</div>
  </div>
);
