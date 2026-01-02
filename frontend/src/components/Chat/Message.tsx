/**
 * Message component - renders different message types with intermediate steps
 */
import type { ReactNode } from "react";
import type { SSEEventData } from "../../types/events";
import { CodeBlock } from "./CodeBlock";
import { MessageActions } from "./MessageActions";

interface MessageProps {
  event: SSEEventData;
  onRegenerate?: () => void;
}

const MessageWrapper = ({
  children,
}: {
  children: ReactNode;
}) => (
  <div className="py-4 animate-fade-in">
    <div className="bg-card border border-border/70 rounded-3xl p-5 shadow-sm space-y-3">
      {children}
    </div>
  </div>
);

const SectionHeader = ({
  children,
  emoji,
}: {
  children: ReactNode;
  emoji?: string;
}) => (
  <div className="text-base font-semibold text-foreground flex items-center gap-2">
    {emoji && <span>{emoji}</span>}
    {children}
  </div>
);

export const Message = ({ event, onRegenerate }: MessageProps) => {
  switch (event.type) {
    case "user_query":
      return (
        <div className="flex justify-end mb-6 animate-fade-in">
          <div className="max-w-[70%] rounded-3xl bg-secondary/80 px-4 py-2.5 text-[15px] text-foreground shadow-sm">
            {event.data.query}
          </div>
        </div>
      );

    case "planning":
      return (
        <MessageWrapper>
          <SectionHeader emoji="📋">Planning</SectionHeader>
          <div className="space-y-4 text-sm">
            <div>
              <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5">
                Problem Understanding
              </div>
              <p className="leading-relaxed m-0 text-foreground">
                {event.data.understanding}
              </p>
            </div>
            <div>
              <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5">
                Approach
              </div>
              <p className="leading-relaxed m-0 text-foreground">
                {event.data.approach}
              </p>
            </div>
          </div>
        </MessageWrapper>
      );

    case "test_inference_skipped":
      return (
        <MessageWrapper>
          <SectionHeader emoji="⏭️">Test Inference Skipped</SectionHeader>
          <p className="text-sm text-muted-foreground m-0">
            {event.data.message} ({event.data.test_count} test
            {event.data.test_count !== 1 ? "s" : ""})
          </p>
        </MessageWrapper>
      );

    case "test_inference":
      return (
        <MessageWrapper>
          <SectionHeader emoji="🧪">
            Generated {event.data.count} Test Cases
          </SectionHeader>
          <div className="space-y-2">
            {event.data.test_cases.map((test, idx) => (
              <div
                key={idx}
                className="bg-secondary/70 rounded-2xl p-3 border border-border/60"
              >
                <div className="text-sm text-foreground mb-1">
                  {test.description}
                </div>
                <div className="text-xs text-muted-foreground font-mono">
                  Inputs: {JSON.stringify(test.inputs)} → Expected:{" "}
                  {JSON.stringify(test.expected_output)}
                </div>
              </div>
            ))}
          </div>
        </MessageWrapper>
      );

    case "code_generated":
      return (
        <MessageWrapper>
          <SectionHeader emoji="💻">
            Code Generated (v{event.data.version}, iteration{" "}
            {event.data.iteration})
          </SectionHeader>
          <CodeBlock code={event.data.code} language="python" />
          <MessageActions onRegenerate={onRegenerate} />
        </MessageWrapper>
      );

    case "execution":
      const executionIcon = event.data.success ? "✅" : "❌";
      return (
        <MessageWrapper>
          <SectionHeader emoji={executionIcon}>
            {event.data.success ? "Execution Successful" : "Execution Failed"}
          </SectionHeader>
          <div className="space-y-2">
            {event.data.output && (
              <div className="bg-secondary/70 rounded-2xl p-4 border border-border/60">
                <div className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
                  Output
                </div>
                <pre className="text-sm text-foreground font-mono m-0 whitespace-pre-wrap">
                  {event.data.output}
                </pre>
              </div>
            )}
            {event.data.error && (
              <div className="bg-red-500/10 rounded-2xl p-4 border border-red-500/40">
                <div className="text-xs font-medium text-red-400 uppercase tracking-wide mb-2">
                  Error
                </div>
                <pre className="text-sm text-red-200 font-mono m-0 whitespace-pre-wrap">
                  {event.data.error}
                </pre>
              </div>
            )}
            <div className="text-xs text-muted-foreground">
              Execution time: {event.data.execution_time.toFixed(3)}s
              {event.data.timed_out && " (timed out)"}
            </div>
          </div>
        </MessageWrapper>
      );

    case "validation":
      const allPassed = event.data.failed === 0;
      const validationIcon = allPassed ? "✅" : "⚠️";
      return (
        <MessageWrapper>
          <SectionHeader emoji="🧪">
            Validation: {event.data.passed}/{event.data.total} tests passed
          </SectionHeader>
          <div className="space-y-2">
            {event.data.results.map((result, idx) => (
              <div
                key={idx}
                className={`rounded-2xl p-3 border ${
                  result.passed
                    ? "border-emerald-500/40 bg-emerald-500/5"
                    : "border-red-500/40 bg-red-500/5"
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span>{result.passed ? "✅" : "❌"}</span>
                  <span className="text-sm text-foreground">
                    {result.description}
                  </span>
                </div>
                {!result.passed && (
                  <div className="text-xs text-muted-foreground ml-6 mt-1 font-mono space-y-0.5">
                    <div>
                      Expected: {JSON.stringify(result.expected_output)}
                    </div>
                    {result.actual_output && (
                      <div>Got: {result.actual_output}</div>
                    )}
                    {result.error && <div>Error: {result.error}</div>}
                  </div>
                )}
              </div>
            ))}
          </div>
        </MessageWrapper>
      );

    case "error_fixing":
      return (
        <MessageWrapper>
          <SectionHeader emoji="🔧">
            Error Analysis (iteration {event.data.iteration})
          </SectionHeader>
          <pre className="text-sm text-muted-foreground whitespace-pre-wrap bg-secondary/70 rounded-2xl p-4 border border-border/60 font-mono m-0">
            {event.data.analysis}
          </pre>
        </MessageWrapper>
      );

    case "complete":
      const completeIcon = event.data.success ? "🎉" : "❌";
      return (
        <MessageWrapper>
          <SectionHeader emoji={completeIcon}>
            {event.data.success ? "Success!" : "Failed"}
          </SectionHeader>
          <div className="space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-foreground font-medium">Reason:</span>{" "}
                <span className="text-muted-foreground">{event.data.reason}</span>
              </div>
              <div>
                <span className="text-foreground font-medium">Tests:</span>{" "}
                <span className="text-muted-foreground">
                  {event.data.passed_tests}/{event.data.total_tests} passed
                </span>
              </div>
              <div>
                <span className="text-foreground font-medium">
                  Iterations:
                </span>{" "}
                <span className="text-muted-foreground">{event.data.iterations}</span>
              </div>
              <div>
                <span className="text-foreground font-medium">Tokens:</span>{" "}
                <span className="text-muted-foreground">
                  {event.data.token_usage.total_tokens} ($
                  {event.data.token_usage.estimated_cost_usd.toFixed(4)})
                </span>
              </div>
            </div>
          </div>
          {event.data.final_code && (
            <div className="mt-4">
              <div className="text-sm font-medium text-muted-foreground mb-2">
                Final Code
              </div>
              <CodeBlock code={event.data.final_code} language="python" />
              <MessageActions onRegenerate={onRegenerate} />
            </div>
          )}
        </MessageWrapper>
      );

    case "error":
      return (
        <MessageWrapper>
          <SectionHeader emoji="❌">Error</SectionHeader>
          <div className="text-sm text-red-200 bg-red-500/10 rounded-2xl p-4 border border-red-500/40">
            {event.data.error}
          </div>
        </MessageWrapper>
      );

    default:
      return null;
  }
};
