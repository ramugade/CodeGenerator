/**
 * Message component - renders different message types with Claude.ai-like styling
 */
import type { SSEEventData } from '../../types/events';
import { CodeBlock } from '../Code/CodeBlock';
import { ExecutionLog } from '../Code/ExecutionLog';

interface MessageProps {
  event: SSEEventData;
}

const MessageWrapper = ({ children, icon = '🤖' }: { children: React.ReactNode; icon?: string }) => (
  <div className="flex items-start gap-4 py-6 border-b border-gray-200 dark:border-gray-800">
    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0 shadow-sm">
      <span className="text-white text-sm">{icon}</span>
    </div>
    <div className="flex-1 min-w-0">
      {children}
    </div>
  </div>
);

const UserMessageWrapper = ({ children }: { children: React.ReactNode }) => (
  <div className="flex items-start gap-4 py-6 border-b border-gray-200 dark:border-gray-800">
    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0 shadow-sm">
      <span className="text-white text-sm">👤</span>
    </div>
    <div className="flex-1 min-w-0">
      {children}
    </div>
  </div>
);

const SectionHeader = ({ children, emoji }: { children: React.ReactNode; emoji?: string }) => (
  <div className="text-gray-700 dark:text-gray-300 font-semibold mb-3 flex items-center gap-2">
    {emoji && <span>{emoji}</span>}
    {children}
  </div>
);

export const Message = ({ event }: MessageProps) => {
  switch (event.type) {
    case 'user_query':
      return (
        <UserMessageWrapper>
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-800 dark:text-gray-100 whitespace-pre-wrap m-0">{event.data.query}</p>
          </div>
        </UserMessageWrapper>
      );

    case 'planning':
      return (
        <MessageWrapper icon="📋">
          <SectionHeader emoji="📋">Planning</SectionHeader>
          <div className="space-y-4 text-gray-700 dark:text-gray-300">
            <div>
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1.5">Problem Understanding</div>
              <p className="text-sm leading-relaxed m-0">{event.data.understanding}</p>
            </div>
            <div>
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1.5">Approach</div>
              <p className="text-sm leading-relaxed m-0">{event.data.approach}</p>
            </div>
          </div>
        </MessageWrapper>
      );

    case 'test_inference_skipped':
      return (
        <MessageWrapper icon="⏭️">
          <SectionHeader emoji="⏭️">Test Inference Skipped</SectionHeader>
          <p className="text-gray-700 dark:text-gray-300 text-sm m-0">
            {event.data.message} ({event.data.test_count} test{event.data.test_count !== 1 ? 's' : ''})
          </p>
        </MessageWrapper>
      );

    case 'test_inference':
      return (
        <MessageWrapper icon="🧪">
          <SectionHeader emoji="🧪">Generated {event.data.count} Test Cases</SectionHeader>
          <div className="space-y-2">
            {event.data.test_cases.map((test, idx) => (
              <div key={idx} className="bg-gray-100 dark:bg-gray-800/40 rounded-lg p-3 border border-gray-300 dark:border-gray-700/50">
                <div className="text-sm text-gray-800 dark:text-gray-200 mb-1">{test.description}</div>
                <div className="text-xs text-gray-600 dark:text-gray-500 font-mono">
                  Inputs: {JSON.stringify(test.inputs)} → Expected: {JSON.stringify(test.expected_output)}
                </div>
              </div>
            ))}
          </div>
        </MessageWrapper>
      );

    case 'code_generated':
      return (
        <MessageWrapper icon="💻">
          <SectionHeader emoji="💻">
            Code Generated (v{event.data.version}, iteration {event.data.iteration})
          </SectionHeader>
          <CodeBlock code={event.data.code} />
        </MessageWrapper>
      );

    case 'execution':
      const executionIcon = event.data.success ? '✅' : '❌';
      return (
        <MessageWrapper icon={executionIcon}>
          <SectionHeader emoji={executionIcon}>
            {event.data.success ? 'Execution Successful' : 'Execution Failed'}
          </SectionHeader>
          <ExecutionLog
            output={event.data.output}
            error={event.data.error}
            executionTime={event.data.execution_time}
            timedOut={event.data.timed_out}
          />
        </MessageWrapper>
      );

    case 'validation':
      const allPassed = event.data.failed === 0;
      const validationIcon = allPassed ? '✅' : '⚠️';
      return (
        <MessageWrapper icon={validationIcon}>
          <SectionHeader emoji="🧪">
            Validation: {event.data.passed}/{event.data.total} tests passed
          </SectionHeader>
          <div className="space-y-2">
            {event.data.results.map((result, idx) => (
              <div
                key={idx}
                className={`rounded-lg p-3 border ${
                  result.passed
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700/30'
                    : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700/30'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span>{result.passed ? '✅' : '❌'}</span>
                  <span className="text-sm text-gray-800 dark:text-gray-200">{result.description}</span>
                </div>
                {!result.passed && (
                  <div className="text-xs text-gray-600 dark:text-gray-400 ml-6 mt-1 font-mono">
                    Expected: {JSON.stringify(result.expected_output)}
                    {result.actual_output && `, Got: ${result.actual_output}`}
                    {result.error && `, Error: ${result.error}`}
                  </div>
                )}
              </div>
            ))}
          </div>
        </MessageWrapper>
      );

    case 'error_fixing':
      return (
        <MessageWrapper icon="🔧">
          <SectionHeader emoji="🔧">
            Error Analysis (iteration {event.data.iteration})
          </SectionHeader>
          <pre className="text-gray-700 dark:text-gray-300 text-sm whitespace-pre-wrap
                          bg-gray-100 dark:bg-gray-800/40 rounded-lg p-4
                          border border-gray-300 dark:border-gray-700/50 font-mono m-0">
            {event.data.analysis}
          </pre>
        </MessageWrapper>
      );

    case 'complete':
      const completeIcon = event.data.success ? '🎉' : '❌';
      return (
        <MessageWrapper icon={completeIcon}>
          <SectionHeader emoji={completeIcon}>
            {event.data.success ? 'Success!' : 'Failed'}
          </SectionHeader>
          <div className="space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-gray-500 dark:text-gray-400">Reason:</span>
                <span className="text-gray-800 dark:text-gray-200 ml-2">{event.data.reason}</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Tests:</span>
                <span className="text-gray-800 dark:text-gray-200 ml-2">
                  {event.data.passed_tests}/{event.data.total_tests} passed
                </span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Iterations:</span>
                <span className="text-gray-800 dark:text-gray-200 ml-2">{event.data.iterations}</span>
              </div>
              <div>
                <span className="text-gray-500 dark:text-gray-400">Tokens:</span>
                <span className="text-gray-800 dark:text-gray-200 ml-2">
                  {event.data.token_usage.total_tokens} (${event.data.token_usage.estimated_cost_usd.toFixed(4)})
                </span>
              </div>
            </div>
          </div>
          {event.data.final_code && (
            <div className="mt-4">
              <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Final Code</div>
              <CodeBlock code={event.data.final_code} />
            </div>
          )}
        </MessageWrapper>
      );

    case 'error':
      return (
        <MessageWrapper icon="❌">
          <SectionHeader emoji="❌">Error</SectionHeader>
          <div className="text-red-700 dark:text-red-300 text-sm
                          bg-red-50 dark:bg-red-900/20 rounded-lg p-4
                          border border-red-300 dark:border-red-700/30">
            {event.data.error}
          </div>
        </MessageWrapper>
      );

    default:
      return null;
  }
};
