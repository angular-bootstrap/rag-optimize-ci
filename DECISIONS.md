# Design Decisions

## 1. CI-first before dashboard
Decision: prioritize GitHub Action + CLI over web UI.
Reason: strongest immediate value for startup teams and highest hiring signal.

## 2. RAG-only scope
Decision: optimize only RAG QA workflows in v1.
Reason: clear product identity beats broad generic evaluation.

## 3. Weighted score + hard constraints
Decision: rank with weighted score after enforcing quality/latency/cost thresholds.
Reason: mirrors real shipping criteria where safety rails must be non-negotiable.

## 4. Mock adapter in v1
Decision: include deterministic mock provider first.
Reason: keeps project reproducible, low-cost, and testable in CI without external API keys.

## 5. JSON artifacts as source of truth
Decision: persist run artifacts as JSON in `artifacts/`.
Reason: easy regression diffing, reproducibility, and auditability.
