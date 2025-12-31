import { useChatStore } from '../../store/chatStore';

export const CostCounter = () => {
  const { currentSessionCost, currentSessionTokens } = useChatStore();

  return (
    <div className="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 text-sm">
        <span className="text-green-600 dark:text-green-400 font-semibold font-mono">
          ${currentSessionCost.toFixed(4)}
        </span>
        <span className="text-gray-400 dark:text-gray-600">•</span>
        <span className="text-gray-600 dark:text-gray-400 font-mono text-xs">
          {currentSessionTokens.toLocaleString()} tokens
        </span>
      </div>
    </div>
  );
};
