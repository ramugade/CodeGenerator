import { useState, useEffect } from "react";
import { ChevronDown, Coins, Check } from "lucide-react";
import { modelAPI } from "../../services/api";

interface ChatHeaderProps {
  cost?: number;
  tokens?: number;
  selectedModel?: string;
  onModelChange?: (modelId: string) => void;
}

interface Model {
  id: string;
  name: string;
  provider: string;
  input_cost: number;
  output_cost: number;
  category: string;
}

interface ModelGroup {
  label: string;
  models: Array<{
    id: string;
    name: string;
    price: string;
  }>;
}

export const ChatHeader = ({ cost = 0, tokens = 0, selectedModel: externalSelectedModel, onModelChange }: ChatHeaderProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState(externalSelectedModel || "gpt-3.5-turbo");
  const [modelGroups, setModelGroups] = useState<ModelGroup[]>([]);

  useEffect(() => {
    modelAPI.listModels()
      .then((data) => {
        const models = data.models || [];

        // Group models by category
        const grouped = models.reduce((acc: Record<string, Model[]>, model: Model) => {
          if (!acc[model.category]) {
            acc[model.category] = [];
          }
          acc[model.category].push(model);
          return acc;
        }, {});

        // Transform to the format needed for rendering
        const groups: ModelGroup[] = Object.entries(grouped).map(([label, models]) => ({
          label,
          models: models.map((m) => ({
            id: m.id,
            name: m.name,
            price: `$${m.input_cost}/$${m.output_cost} per 1M tokens`
          }))
        }));

        setModelGroups(groups);
      })
      .catch((error) => console.error("Failed to load models:", error));
  }, []);

  const getSelectedModelName = () => {
    for (const group of modelGroups) {
      const model = group.models.find((m) => m.id === selectedModel);
      if (model) return model.name;
    }
    return "Select Model";
  };

  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-border/50">
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-accent transition-colors"
        >
          <span className="font-medium text-foreground">{getSelectedModelName()}</span>
          <ChevronDown size={16} className={`text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`} />
        </button>

        {/* Dropdown */}
        {isOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
            <div className="absolute top-full left-0 mt-2 w-80 bg-popover border border-border rounded-xl shadow-xl z-50 overflow-hidden animate-fade-in">
              <div className="max-h-96 overflow-y-auto scrollbar-thin py-2">
                {modelGroups.map((group) => (
                  <div key={group.label}>
                    <div className="px-3 py-2 text-xs font-medium text-muted-foreground">
                      {group.label}
                    </div>
                    {group.models.map((model) => (
                      <button
                        key={model.id}
                        onClick={() => {
                          setSelectedModel(model.id);
                          if (onModelChange) {
                            onModelChange(model.id);
                          }
                          setIsOpen(false);
                        }}
                        className="w-full flex items-center gap-3 px-3 py-2 hover:bg-accent transition-colors text-left"
                      >
                        <div className="w-4 flex-shrink-0">
                          {selectedModel === model.id && (
                            <Check size={14} className="text-primary" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm text-foreground">{model.name}</div>
                          <div className="text-xs text-muted-foreground">{model.price}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Cost and token display */}
      <div className="flex items-center gap-3 px-3 py-1.5 bg-secondary rounded-lg">
        <div className="flex items-center gap-1.5 text-sm">
          <Coins size={14} className="text-primary" />
          <span className="text-muted-foreground">Tokens:</span>
          <span className="font-medium text-foreground">{tokens.toLocaleString()}</span>
        </div>
        <div className="w-px h-4 bg-border" />
        <div className="flex items-center gap-1.5 text-sm">
          <span className="text-muted-foreground">Cost:</span>
          <span className="font-medium text-primary">${cost.toFixed(4)}</span>
        </div>
      </div>
    </header>
  );
};
