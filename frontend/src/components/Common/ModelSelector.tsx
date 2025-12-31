import { AVAILABLE_MODELS, formatCost, getModelById } from '../../config/models';

interface ModelSelectorProps {
  selectedModel: string;
  onChange: (modelId: string, provider: 'openai' | 'anthropic') => void;
  disabled?: boolean;
}

export const ModelSelector = ({ selectedModel, onChange, disabled }: ModelSelectorProps) => {
  // Group models by category
  const groupedModels = AVAILABLE_MODELS.reduce((acc, model) => {
    if (!acc[model.category]) {
      acc[model.category] = [];
    }
    acc[model.category].push(model);
    return acc;
  }, {} as Record<string, typeof AVAILABLE_MODELS>);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const modelId = e.target.value;
    const model = getModelById(modelId);
    if (model) {
      onChange(modelId, model.provider);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-gray-400 dark:text-gray-500">Model:</label>
      <select
        value={selectedModel}
        onChange={handleChange}
        disabled={disabled}
        className="bg-gray-800 dark:bg-gray-700 text-gray-100 dark:text-gray-200 rounded-lg px-3 py-1.5 text-sm
                   focus:outline-none focus:ring-2 focus:ring-blue-500
                   disabled:opacity-50 disabled:cursor-not-allowed
                   border border-gray-700 dark:border-gray-600"
      >
        {Object.entries(groupedModels).map(([category, models]) => (
          <optgroup key={category} label={category}>
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name} ({formatCost(model.inputCost, model.outputCost)})
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
};
