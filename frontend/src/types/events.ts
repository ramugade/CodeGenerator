/**
 * TypeScript types for SSE events from backend
 */

export interface TestCase {
  description: string;
  inputs: Record<string, any>;
  expected_output: any;
}

export interface PlanningEvent {
  understanding: string;
  approach: string;
}

export interface TestInferenceEvent {
  test_cases: TestCase[];
  count: number;
}

export interface TestInferenceSkippedEvent {
  message: string;
  test_count: number;
}

export interface CodeGeneratedEvent {
  code: string;
  version: number;
  iteration: number;
}

export interface ExecutionEvent {
  success: boolean;
  output?: string;
  error?: string;
  execution_time: number;
  timed_out: boolean;
}

export interface ValidationResult {
  description: string;
  passed: boolean;
  actual_output?: string;
  expected_output: any;
  error?: string;
}

export interface ValidationEvent {
  passed: number;
  failed: number;
  total: number;
  results: ValidationResult[];
}

export interface ErrorFixingEvent {
  analysis: string;
  iteration: number;
}

export interface CompleteEvent {
  success: boolean;
  reason: string;
  final_code?: string;
  final_output?: string;
  iterations: number;
  passed_tests: number;
  total_tests: number;
  token_usage: {
    total_tokens: number;
    estimated_cost_usd: number;
    breakdown: Record<string, any>;
  };
}

export interface ErrorEvent {
  error: string;
}

export type SSEEventData =
  | { type: 'planning'; data: PlanningEvent }
  | { type: 'test_inference'; data: TestInferenceEvent }
  | { type: 'test_inference_skipped'; data: TestInferenceSkippedEvent }
  | { type: 'code_generated'; data: CodeGeneratedEvent }
  | { type: 'execution'; data: ExecutionEvent }
  | { type: 'validation'; data: ValidationEvent }
  | { type: 'error_fixing'; data: ErrorFixingEvent }
  | { type: 'complete'; data: CompleteEvent }
  | { type: 'error'; data: ErrorEvent };

export interface GenerateRequest {
  query: string;
  llm_provider: 'openai' | 'anthropic';
  user_provided_tests?: TestCase[];
  max_iterations?: number;
}
