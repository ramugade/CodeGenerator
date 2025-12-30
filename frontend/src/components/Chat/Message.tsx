/**
 * Message component - renders different message types
 */
import type { SSEEventData } from '../../types/events';
import { CodeBlock } from '../Code/CodeBlock';
import { ExecutionLog } from '../Code/ExecutionLog';

interface MessageProps {
  event: SSEEventData;
}

export const Message = ({ event }: MessageProps) => {
  switch (event.type) {
    case 'planning':
      return (
        <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
          <div className="text-blue-400 font-semibold mb-2">📋 Planning</div>
          <div className="space-y-3">
            <div>
              <div className="text-sm text-gray-400 mb-1">Problem Understanding:</div>
              <div className="text-gray-200 text-sm">{event.data.understanding}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Approach:</div>
              <div className="text-gray-200 text-sm">{event.data.approach}</div>
            </div>
          </div>
        </div>
      );

    case 'test_inference_skipped':
      return (
        <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
          <div className="text-purple-400 font-semibold mb-2">⏭️ Test Inference Skipped</div>
          <div className="text-gray-200 text-sm">
            {event.data.message} ({event.data.test_count} test{event.data.test_count !== 1 ? 's' : ''})
          </div>
        </div>
      );

    case 'test_inference':
      return (
        <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
          <div className="text-purple-400 font-semibold mb-2">
            🧪 Generated {event.data.count} Test Cases
          </div>
          <div className="space-y-2">
            {event.data.test_cases.map((test, idx) => (
              <div key={idx} className="bg-gray-900/50 rounded p-3">
                <div className="text-sm text-gray-300 mb-1">{test.description}</div>
                <div className="text-xs text-gray-500">
                  Inputs: {JSON.stringify(test.inputs)} → Expected: {JSON.stringify(test.expected_output)}
                </div>
              </div>
            ))}
          </div>
        </div>
      );

    case 'code_generated':
      return (
        <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
          <div className="text-green-400 font-semibold mb-2">
            💻 Code Generated (v{event.data.version}, iteration {event.data.iteration})
          </div>
          <CodeBlock code={event.data.code} />
        </div>
      );

    case 'execution':
      return (
        <div className={`border rounded-lg p-4 ${
          event.data.success
            ? 'bg-green-900/20 border-green-500/30'
            : 'bg-red-900/20 border-red-500/30'
        }`}>
          <div className={`font-semibold mb-2 ${
            event.data.success ? 'text-green-400' : 'text-red-400'
          }`}>
            {event.data.success ? '✅ Execution Successful' : '❌ Execution Failed'}
          </div>
          <ExecutionLog
            output={event.data.output}
            error={event.data.error}
            executionTime={event.data.execution_time}
            timedOut={event.data.timed_out}
          />
        </div>
      );

    case 'validation':
      const allPassed = event.data.failed === 0;
      return (
        <div className={`border rounded-lg p-4 ${
          allPassed
            ? 'bg-green-900/20 border-green-500/30'
            : 'bg-yellow-900/20 border-yellow-500/30'
        }`}>
          <div className={`font-semibold mb-2 ${
            allPassed ? 'text-green-400' : 'text-yellow-400'
          }`}>
            🧪 Validation: {event.data.passed}/{event.data.total} tests passed
          </div>
          <div className="space-y-2">
            {event.data.results.map((result, idx) => (
              <div
                key={idx}
                className={`p-3 rounded ${
                  result.passed ? 'bg-green-900/30' : 'bg-red-900/30'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span>{result.passed ? '✅' : '❌'}</span>
                  <span className="text-sm text-gray-300">{result.description}</span>
                </div>
                {!result.passed && (
                  <div className="text-xs text-gray-400 ml-6">
                    Expected: {JSON.stringify(result.expected_output)}
                    {result.actual_output && `, Got: ${result.actual_output}`}
                    {result.error && `, Error: ${result.error}`}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      );

    case 'error_fixing':
      return (
        <div className="bg-orange-900/20 border border-orange-500/30 rounded-lg p-4">
          <div className="text-orange-400 font-semibold mb-2">
            🔧 Error Analysis (iteration {event.data.iteration})
          </div>
          <pre className="text-gray-200 text-sm whitespace-pre-wrap">{event.data.analysis}</pre>
        </div>
      );

    case 'complete':
      return (
        <div className={`border rounded-lg p-4 ${
          event.data.success
            ? 'bg-green-900/20 border-green-500/30'
            : 'bg-red-900/20 border-red-500/30'
        }`}>
          <div className={`font-semibold mb-3 text-lg ${
            event.data.success ? 'text-green-400' : 'text-red-400'
          }`}>
            {event.data.success ? '🎉 Success!' : '❌ Failed'}
          </div>
          <div className="space-y-2 text-sm">
            <div className="text-gray-300">
              Reason: {event.data.reason}
            </div>
            <div className="text-gray-300">
              Tests: {event.data.passed_tests}/{event.data.total_tests} passed
            </div>
            <div className="text-gray-300">
              Iterations: {event.data.iterations}
            </div>
            <div className="text-gray-400">
              Tokens: {event.data.token_usage.total_tokens} (${event.data.token_usage.estimated_cost_usd.toFixed(4)})
            </div>
          </div>
          {event.data.final_code && (
            <div className="mt-4">
              <div className="text-sm text-gray-400 mb-2">Final Code:</div>
              <CodeBlock code={event.data.final_code} />
            </div>
          )}
        </div>
      );

    case 'error':
      return (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
          <div className="text-red-400 font-semibold mb-2">❌ Error</div>
          <div className="text-red-300 text-sm">{event.data.error}</div>
        </div>
      );

    default:
      return null;
  }
};
