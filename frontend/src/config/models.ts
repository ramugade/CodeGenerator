/**
 * LLM model configurations with pricing
 */

export interface ModelConfig {
  id: string;
  name: string;
  provider: 'openai' | 'anthropic';
  inputCost: number;  // per 1M tokens
  outputCost: number; // per 1M tokens
  category: string;
}

export const AVAILABLE_MODELS: ModelConfig[] = [
  // OpenAI Models
  {
    id: 'gpt-4-turbo-preview',
    name: 'GPT-4 Turbo',
    provider: 'openai',
    inputCost: 10.00,
    outputCost: 30.00,
    category: 'OpenAI GPT-4'
  },
  {
    id: 'gpt-4',
    name: 'GPT-4',
    provider: 'openai',
    inputCost: 30.00,
    outputCost: 60.00,
    category: 'OpenAI GPT-4'
  },
  {
    id: 'gpt-3.5-turbo',
    name: 'GPT-3.5 Turbo',
    provider: 'openai',
    inputCost: 0.50,
    outputCost: 1.50,
    category: 'OpenAI GPT-3.5'
  },

  // Anthropic Claude 4.5 (Latest)
  {
    id: 'claude-opus-4-5-20251101',
    name: 'Claude Opus 4.5',
    provider: 'anthropic',
    inputCost: 15.00,
    outputCost: 75.00,
    category: 'Claude 4.5 (Latest)'
  },
  {
    id: 'claude-sonnet-4-5-20250929',
    name: 'Claude Sonnet 4.5',
    provider: 'anthropic',
    inputCost: 3.00,
    outputCost: 15.00,
    category: 'Claude 4.5 (Latest)'
  },
  {
    id: 'claude-haiku-4-5-20251001',
    name: 'Claude Haiku 4.5',
    provider: 'anthropic',
    inputCost: 0.80,
    outputCost: 4.00,
    category: 'Claude 4.5 (Latest)'
  },

  // Anthropic Claude 4
  {
    id: 'claude-opus-4-1-20250805',
    name: 'Claude Opus 4.1',
    provider: 'anthropic',
    inputCost: 15.00,
    outputCost: 75.00,
    category: 'Claude 4'
  },
  {
    id: 'claude-opus-4-20250514',
    name: 'Claude Opus 4',
    provider: 'anthropic',
    inputCost: 15.00,
    outputCost: 75.00,
    category: 'Claude 4'
  },
  {
    id: 'claude-sonnet-4-20250514',
    name: 'Claude Sonnet 4',
    provider: 'anthropic',
    inputCost: 3.00,
    outputCost: 15.00,
    category: 'Claude 4'
  },

  // Anthropic Claude 3.7 and 3.5
  {
    id: 'claude-3-7-sonnet-20250219',
    name: 'Claude 3.7 Sonnet',
    provider: 'anthropic',
    inputCost: 3.00,
    outputCost: 15.00,
    category: 'Claude 3.7 / 3.5'
  },
  {
    id: 'claude-3-5-haiku-20241022',
    name: 'Claude 3.5 Haiku',
    provider: 'anthropic',
    inputCost: 0.80,
    outputCost: 4.00,
    category: 'Claude 3.7 / 3.5'
  },

  // Anthropic Claude 3 (Legacy)
  {
    id: 'claude-3-opus-20240229',
    name: 'Claude 3 Opus',
    provider: 'anthropic',
    inputCost: 15.00,
    outputCost: 75.00,
    category: 'Claude 3 (Legacy)'
  },
  {
    id: 'claude-3-haiku-20240307',
    name: 'Claude 3 Haiku',
    provider: 'anthropic',
    inputCost: 0.25,
    outputCost: 1.25,
    category: 'Claude 3 (Legacy)'
  },
];

// Default models
export const DEFAULT_MODELS = {
  openai: 'gpt-4-turbo-preview',
  anthropic: 'claude-sonnet-4-5-20250929',
};

// Helper to get model by ID
export const getModelById = (id: string): ModelConfig | undefined => {
  return AVAILABLE_MODELS.find(m => m.id === id);
};

// Helper to format cost
export const formatCost = (inputCost: number, outputCost: number): string => {
  return `$${inputCost}/$${outputCost} per 1M tokens`;
};
