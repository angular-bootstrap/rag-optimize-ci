# Case Study: rag-optimize-ci

## Problem
Teams building RAG apps ship prompt/model/retrieval changes quickly but lack a practical CI gate for quality, latency, and cost tradeoffs.

## Solution
`rag-optimize-ci` runs candidate configs against a benchmark dataset and returns:

- candidate scorecard
- recommendation with constraints
- regression verdict vs baseline

## Non-technical explanation

Think of this as a safety check for AI updates.

Before a company changes how its AI assistant answers questions, this tool does a trial run and checks:

- Are answers still good?
- Are answers still based on source documents?
- Is the response too slow?
- Is the response too expensive?

If the new setup is risky, the tool warns the team before customers see the change.

## Everyday example (simple)

A food delivery company has a help assistant in its app.

- Team tries a new AI setup to make replies faster.
- Replies become faster, but some answers are wrong.
- `rag-optimize-ci` catches this in pull request checks.
- Team does not ship the bad update.
- Customers keep getting reliable help answers.

## Architecture

- `ragopt/config.py`: config + dataset loading
- `ragopt/adapters.py`: provider abstraction
- `ragopt/metrics.py`: quality, groundedness, citation, latency/cost scoring
- `ragopt/engine.py`: run pipeline, recommendation, regression comparison
- `ragopt/cli.py`: run/compare/recommend interfaces
- `action.yml`: GitHub Action integration
- `ui/`: React dashboard for visual review of run artifacts

## Core tradeoffs

- Started with deterministic metrics and mock adapter to ensure reliability and reproducibility.
- Deferred complex online judge models and dashboards until CI workflow was complete.

## Impact goals

- Reduce bad RAG releases by catching regressions in PR checks.
- Standardize model/prompt/retriever decisions with transparent scoring.
- Enable lean teams to enforce quality without heavy platform investment.
