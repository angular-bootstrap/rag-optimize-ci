import type { CandidateResult, RunResult } from './types';

export const sortCandidates = (run: RunResult): CandidateResult[] =>
  [...run.candidates].sort((a, b) => b.aggregate.score - a.aggregate.score);

export const formatPct = (value: number): string => `${(value * 100).toFixed(1)}%`;

export const formatMs = (value: number): string => `${value.toFixed(1)} ms`;

export const formatCost = (value: number): string => `$${value.toFixed(5)}`;
