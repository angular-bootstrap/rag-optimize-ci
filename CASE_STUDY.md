# Case Study: rag-optimize-ci

## Problem
Teams building RAG apps ship prompt/model/retrieval changes quickly but lack a practical CI gate for quality, latency, and cost tradeoffs.

## Solution
`rag-optimize-ci` runs candidate configs against a benchmark dataset and returns:

- candidate scorecard
- recommendation with constraints
- regression verdict vs baseline

## Architecture

- `ragopt/config.py`: config + dataset loading
- `ragopt/adapters.py`: provider abstraction
- `ragopt/metrics.py`: quality, groundedness, citation, latency/cost scoring
- `ragopt/engine.py`: run pipeline, recommendation, regression comparison
- `ragopt/cli.py`: run/compare/recommend interfaces
- `action.yml`: GitHub Action integration

## Core tradeoffs

- Started with deterministic metrics and mock adapter to ensure reliability and reproducibility.
- Deferred complex online judge models and dashboards until CI workflow was complete.

## Impact goals

- Reduce bad RAG releases by catching regressions in PR checks.
- Standardize model/prompt/retriever decisions with transparent scoring.
- Enable lean teams to enforce quality without heavy platform investment.
