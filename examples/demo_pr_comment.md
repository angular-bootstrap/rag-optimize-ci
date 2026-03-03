# ragopt run e6f720e2

Dataset: `datasets/rag_qa_small.jsonl`

## Candidate Scorecard

| Candidate | Quality | Grounded | Citation | Latency ms | Cost/query | Score | Constraints |
|---|---:|---:|---:|---:|---:|---:|---|
| baseline-lite | 0.333 | 0.907 | 1.000 | 260.2 | 0.00004 | 0.498 | PASS |
| candidate-detailed | 0.281 | 0.684 | 1.000 | 178.7 | 0.00011 | 0.427 | PASS |

## Recommendation

Winner: `baseline-lite`

baseline-lite has the highest score among candidates that passed hard constraints.
## Regression Report

Baseline: `baseline-lite` vs Candidate: `candidate-detailed`

| Metric | Delta |
|---|---:|
| quality | -0.0526 |
| groundedness | -0.2231 |
| citation | +0.0000 |
| latency_ms | -81.57 |
| cost | +0.000074 |
| score | -0.0708 |

Verdict: **FAIL**