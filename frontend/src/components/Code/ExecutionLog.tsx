/**
 * Execution log display for stdout/stderr
 */
interface ExecutionLogProps {
  output?: string;
  error?: string;
  executionTime?: number;
  timedOut?: boolean;
}

export const ExecutionLog = ({ output, error, executionTime, timedOut }: ExecutionLogProps) => {
  if (!output && !error) {
    return null;
  }

  return (
    <div className="space-y-2">
      {output && (
        <div className="bg-gray-900 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-2">Output:</div>
          <pre className="text-green-400 text-sm font-mono whitespace-pre-wrap">{output}</pre>
        </div>
      )}

      {error && (
        <div className="bg-red-900/20 rounded-lg p-4 border border-red-500/30">
          <div className="text-sm text-red-400 mb-2">
            {timedOut ? 'Timeout Error:' : 'Error:'}
          </div>
          <pre className="text-red-300 text-sm font-mono whitespace-pre-wrap">{error}</pre>
        </div>
      )}

      {executionTime !== undefined && (
        <div className="text-xs text-gray-500">
          Execution time: {executionTime.toFixed(3)}s
        </div>
      )}
    </div>
  );
};
