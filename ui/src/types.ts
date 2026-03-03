export type Weights = {
  quality: number;
  groundedness: number;
  citation: number;
  latency: number;
  cost: number;
};

export type Policy = {
  min_quality: number;
  max_latency_ms: number;
  max_cost_per_query: number;
  max_quality_drop: number;
  weights: Weights;
};

export type CaseMetrics = {
  quality: number;
  groundedness: number;
  citation: number;
  latency_ms: number;
  cost: number;
  score: number;
  passed_hard_constraints: boolean;
};

export type CaseResult = {
  record_id: string;
  answer: string;
  selected_contexts: string[];
  metrics: CaseMetrics;
};

export type CandidateAggregate = {
  quality: number;
  groundedness: number;
  citation: number;
  latency_ms: number;
  cost: number;
  score: number;
  passed_hard_constraints: boolean;
};

export type CandidateResult = {
  name: string;
  provider: string;
  model: string;
  aggregate: CandidateAggregate;
  cases: CaseResult[];
};

export type RunResult = {
  run_id: string;
  generated_at: string;
  dataset_path: string;
  policy: Policy;
  candidates: CandidateResult[];
};
