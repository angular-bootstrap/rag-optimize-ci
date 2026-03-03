from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

from ragopt.models import (
    AppConfig,
    CIConfig,
    CandidateConfig,
    DatasetConfig,
    DatasetRecord,
    MetricsConfig,
    PolicyConfig,
    PricingConfig,
    Weights,
)

_HAS_YAML = importlib.util.find_spec("yaml") is not None
_HAS_PYDANTIC = importlib.util.find_spec("pydantic") is not None


def _parse_structured_text(text: str) -> dict[str, Any]:
    if _HAS_YAML:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("Config root must be a mapping/object")
        return data

    # Fallback parser: expects JSON syntax (which is valid YAML).
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("Config root must be an object")
    return data


def _maybe_validate_with_pydantic(raw: dict[str, Any]) -> dict[str, Any]:
    if not _HAS_PYDANTIC:
        return raw
    try:
        from ragopt.pydantic_models import validate_and_normalize

        return validate_and_normalize(raw)
    except Exception:
        # Keep offline/no-extra-deps mode resilient.
        return raw


def load_config(path: str) -> AppConfig:
    raw = _parse_structured_text(Path(path).read_text())
    raw = _maybe_validate_with_pydantic(raw)

    datasets_raw = raw.get("datasets", {})
    datasets = DatasetConfig(path=datasets_raw["path"], sample_size=datasets_raw.get("sample_size"))

    candidates: list[CandidateConfig] = []
    names = set()
    for c in raw.get("candidates", []):
        name = c["name"]
        if name in names:
            raise ValueError("candidate names must be unique")
        names.add(name)
        candidates.append(
            CandidateConfig(
                name=name,
                provider=c.get("provider", "mock"),
                model=c["model"],
                prompt_template=c.get("prompt_template", "Answer using context. Question: {question}"),
                retriever_top_k=int(c.get("retriever_top_k", 3)),
                chunking_strategy=c.get("chunking_strategy", "fixed"),
                params=c.get("params", {}),
            )
        )
    if not candidates:
        raise ValueError("At least one candidate is required")

    metrics = MetricsConfig(enabled=raw.get("metrics", {}).get("enabled", ["quality", "groundedness", "citation", "latency", "cost"]))

    w_raw = raw.get("policy", {}).get("weights", {})
    weights = Weights(
        quality=float(w_raw.get("quality", 0.45)),
        groundedness=float(w_raw.get("groundedness", 0.25)),
        citation=float(w_raw.get("citation", 0.15)),
        latency=float(w_raw.get("latency", 0.10)),
        cost=float(w_raw.get("cost", 0.05)),
    )
    if any(v < 0 for v in [weights.quality, weights.groundedness, weights.citation, weights.latency, weights.cost]):
        raise ValueError("weights must be non-negative")

    p_raw = raw.get("policy", {})
    policy = PolicyConfig(
        min_quality=float(p_raw.get("min_quality", 0.60)),
        max_latency_ms=float(p_raw.get("max_latency_ms", 2500.0)),
        max_cost_per_query=float(p_raw.get("max_cost_per_query", 0.02)),
        max_quality_drop=float(p_raw.get("max_quality_drop", 0.05)),
        weights=weights,
    )

    ci_raw = raw.get("ci", {})
    mode = ci_raw.get("mode", "fail")
    if mode not in {"fail", "warn"}:
        raise ValueError("ci.mode must be 'fail' or 'warn'")
    ci = CIConfig(mode=mode, post_pr_comment=bool(ci_raw.get("post_pr_comment", True)))

    pricing: dict[str, PricingConfig] = {}
    for model, pr in raw.get("pricing", {}).items():
        pricing[model] = PricingConfig(
            input_per_1k=float(pr.get("input_per_1k", 0.001)),
            output_per_1k=float(pr.get("output_per_1k", 0.002)),
        )

    return AppConfig(datasets=datasets, candidates=candidates, metrics=metrics, policy=policy, ci=ci, pricing=pricing)


def load_dataset(path: str, sample_size: int | None = None) -> list[DatasetRecord]:
    p = Path(path)
    records: list[DatasetRecord] = []
    if p.suffix.lower() == ".jsonl":
        for line in p.read_text().splitlines():
            if line.strip():
                obj = json.loads(line)
                records.append(
                    DatasetRecord(
                        id=obj["id"],
                        question=obj["question"],
                        reference_answer=obj["reference_answer"],
                        contexts=obj.get("contexts", []),
                    )
                )
    elif p.suffix.lower() == ".json":
        data = json.loads(p.read_text())
        for obj in data:
            records.append(
                DatasetRecord(
                    id=obj["id"],
                    question=obj["question"],
                    reference_answer=obj["reference_answer"],
                    contexts=obj.get("contexts", []),
                )
            )
    else:
        raise ValueError("Dataset must be .json or .jsonl")

    return records[:sample_size] if sample_size is not None else records
