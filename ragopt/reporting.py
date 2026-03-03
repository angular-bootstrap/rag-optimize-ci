from __future__ import annotations

from pathlib import Path

from ragopt.models import Recommendation, RegressionReport, RunResult


def build_run_markdown(result: RunResult, rec: Recommendation) -> str:
    lines = []
    lines.append(f"# ragopt run {result.run_id}")
    lines.append("")
    lines.append(f"Dataset: `{result.dataset_path}`")
    lines.append("")
    lines.append("## Candidate Scorecard")
    lines.append("")
    lines.append("| Candidate | Quality | Grounded | Citation | Latency ms | Cost/query | Score | Constraints |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for c in sorted(result.candidates, key=lambda x: x.aggregate.score, reverse=True):
        lines.append(
            f"| {c.name} | {c.aggregate.quality:.3f} | {c.aggregate.groundedness:.3f} | {c.aggregate.citation:.3f} "
            f"| {c.aggregate.latency_ms:.1f} | {c.aggregate.cost:.5f} | {c.aggregate.score:.3f} "
            f"| {'PASS' if c.aggregate.passed_hard_constraints else 'FAIL'} |"
        )

    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(f"Winner: `{rec.winner}`" if rec.winner else "Winner: `none`")
    lines.append("")
    lines.append(rec.reason)
    lines.append("")
    return "\n".join(lines)


def build_regression_markdown(report: RegressionReport) -> str:
    lines = []
    lines.append("## Regression Report")
    lines.append("")
    lines.append(f"Baseline: `{report.baseline_candidate}` vs Candidate: `{report.candidate}`")
    lines.append("")
    lines.append("| Metric | Delta |")
    lines.append("|---|---:|")
    lines.append(f"| quality | {report.deltas.quality:+.4f} |")
    lines.append(f"| groundedness | {report.deltas.groundedness:+.4f} |")
    lines.append(f"| citation | {report.deltas.citation:+.4f} |")
    lines.append(f"| latency_ms | {report.deltas.latency_ms:+.2f} |")
    lines.append(f"| cost | {report.deltas.cost:+.6f} |")
    lines.append(f"| score | {report.deltas.score:+.4f} |")
    lines.append("")
    lines.append(f"Verdict: **{report.verdict.upper()}**")
    return "\n".join(lines)


def write_report(path: str, body: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
