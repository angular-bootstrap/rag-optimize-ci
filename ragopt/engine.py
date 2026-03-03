from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ragopt.adapters import get_adapter
from ragopt.config import load_dataset
from ragopt.metrics import citation_hit_rate, estimate_cost, groundedness, overlap_f1, overall_score
from ragopt.models import (
    AppConfig,
    CandidateAggregate,
    CandidateResult,
    CaseMetrics,
    CaseResult,
    Recommendation,
    RegressionDelta,
    RegressionReport,
    RunResult,
)


def run_evaluation(config: AppConfig, artifacts_dir: str = "artifacts") -> RunResult:
    dataset = load_dataset(config.datasets.path, config.datasets.sample_size)
    if not dataset:
        raise ValueError("Dataset is empty")

    run_id = uuid.uuid4().hex[:8]
    candidate_results: list[CandidateResult] = []

    for candidate in config.candidates:
        adapter = get_adapter(candidate.provider)
        case_results: list[CaseResult] = []

        for record in dataset:
            selected_contexts = record.contexts[: candidate.retriever_top_k]
            gen = adapter.generate(record.question, selected_contexts, candidate.prompt_template, candidate.model, candidate.params)

            q = overlap_f1(gen.answer, record.reference_answer)
            g = groundedness(gen.answer, selected_contexts)
            c = citation_hit_rate(gen.answer, selected_contexts)

            pricing = config.pricing.get(candidate.model)
            in_rate = pricing.input_per_1k if pricing else 0.001
            out_rate = pricing.output_per_1k if pricing else 0.002
            cost = estimate_cost(gen.input_tokens, gen.output_tokens, in_rate, out_rate)

            score = overall_score(
                quality=q,
                groundedness_score=g,
                citation=c,
                latency_ms=gen.latency_ms,
                cost=cost,
                max_latency_ms=config.policy.max_latency_ms,
                max_cost=config.policy.max_cost_per_query,
                w_quality=config.policy.weights.quality,
                w_groundedness=config.policy.weights.groundedness,
                w_citation=config.policy.weights.citation,
                w_latency=config.policy.weights.latency,
                w_cost=config.policy.weights.cost,
            )
            passed = q >= config.policy.min_quality and gen.latency_ms <= config.policy.max_latency_ms and cost <= config.policy.max_cost_per_query

            case_results.append(
                CaseResult(
                    record_id=record.id,
                    answer=gen.answer,
                    selected_contexts=selected_contexts,
                    metrics=CaseMetrics(
                        quality=q,
                        groundedness=g,
                        citation=c,
                        latency_ms=gen.latency_ms,
                        cost=cost,
                        score=score,
                        passed_hard_constraints=passed,
                    ),
                )
            )

        n = len(case_results)
        agg_quality = sum(c.metrics.quality for c in case_results) / n
        agg_groundedness = sum(c.metrics.groundedness for c in case_results) / n
        agg_citation = sum(c.metrics.citation for c in case_results) / n
        agg_latency = sum(c.metrics.latency_ms for c in case_results) / n
        agg_cost = sum(c.metrics.cost for c in case_results) / n
        agg_score = sum(c.metrics.score for c in case_results) / n
        passed = agg_quality >= config.policy.min_quality and agg_latency <= config.policy.max_latency_ms and agg_cost <= config.policy.max_cost_per_query

        candidate_results.append(
            CandidateResult(
                name=candidate.name,
                provider=candidate.provider,
                model=candidate.model,
                aggregate=CandidateAggregate(
                    quality=agg_quality,
                    groundedness=agg_groundedness,
                    citation=agg_citation,
                    latency_ms=agg_latency,
                    cost=agg_cost,
                    score=agg_score,
                    passed_hard_constraints=passed,
                ),
                cases=case_results,
            )
        )

    result = RunResult(
        run_id=run_id,
        generated_at=datetime.now(timezone.utc).isoformat(),
        dataset_path=config.datasets.path,
        policy=config.policy,
        candidates=candidate_results,
    )

    out_dir = Path(artifacts_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"run_{run_id}.json").write_text(json.dumps(asdict(result), indent=2))
    return result


def recommend(result: RunResult) -> Recommendation:
    passing = [c for c in result.candidates if c.aggregate.passed_hard_constraints]
    ranked = sorted(result.candidates, key=lambda c: c.aggregate.score, reverse=True)
    ranking = [c.name for c in ranked]

    if not passing:
        return Recommendation(winner=None, reason="No candidate passed hard constraints (quality/latency/cost).", ranking=ranking)

    winner = sorted(passing, key=lambda c: c.aggregate.score, reverse=True)[0]
    return Recommendation(
        winner=winner.name,
        reason=f"{winner.name} has the highest score among candidates that passed hard constraints.",
        ranking=ranking,
    )


def _from_dict_run(raw: dict[str, Any]) -> RunResult:
    policy_raw = raw["policy"]
    from ragopt.models import PolicyConfig, Weights, CandidateAggregate, CaseMetrics, CaseResult, CandidateResult

    policy = PolicyConfig(
        min_quality=policy_raw["min_quality"],
        max_latency_ms=policy_raw["max_latency_ms"],
        max_cost_per_query=policy_raw["max_cost_per_query"],
        max_quality_drop=policy_raw.get("max_quality_drop", 0.05),
        weights=Weights(**policy_raw["weights"]),
    )

    candidates: list[CandidateResult] = []
    for c in raw["candidates"]:
        cases = [
            CaseResult(
                record_id=case["record_id"],
                answer=case["answer"],
                selected_contexts=case["selected_contexts"],
                metrics=CaseMetrics(**case["metrics"]),
            )
            for case in c["cases"]
        ]
        candidates.append(
            CandidateResult(
                name=c["name"],
                provider=c["provider"],
                model=c["model"],
                aggregate=CandidateAggregate(**c["aggregate"]),
                cases=cases,
            )
        )

    return RunResult(
        run_id=raw["run_id"],
        generated_at=raw["generated_at"],
        dataset_path=raw["dataset_path"],
        policy=policy,
        candidates=candidates,
    )


def load_run(path: str) -> RunResult:
    return _from_dict_run(json.loads(Path(path).read_text()))


def compare_runs(baseline: RunResult, candidate: RunResult, baseline_name: str, candidate_name: str) -> RegressionReport:
    b = _find_candidate(baseline, baseline_name)
    c = _find_candidate(candidate, candidate_name)

    deltas = RegressionDelta(
        quality=c.aggregate.quality - b.aggregate.quality,
        groundedness=c.aggregate.groundedness - b.aggregate.groundedness,
        citation=c.aggregate.citation - b.aggregate.citation,
        latency_ms=c.aggregate.latency_ms - b.aggregate.latency_ms,
        cost=c.aggregate.cost - b.aggregate.cost,
        score=c.aggregate.score - b.aggregate.score,
    )

    quality_drop = b.aggregate.quality - c.aggregate.quality
    breached = quality_drop > candidate.policy.max_quality_drop
    verdict = "fail" if breached else "pass"

    return RegressionReport(
        baseline_candidate=baseline_name,
        candidate=candidate_name,
        deltas=deltas,
        breached=breached,
        verdict=verdict,
    )


def _find_candidate(run: RunResult, name: str) -> CandidateResult:
    for c in run.candidates:
        if c.name == name:
            return c
    raise ValueError(f"Candidate '{name}' not found in run {run.run_id}")
