from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class DatasetConfig:
    path: str
    sample_size: int | None = None


@dataclass
class CandidateConfig:
    name: str
    provider: str
    model: str
    prompt_template: str
    retriever_top_k: int
    chunking_strategy: str
    params: dict[str, Any]


@dataclass
class Weights:
    quality: float = 0.45
    groundedness: float = 0.25
    citation: float = 0.15
    latency: float = 0.10
    cost: float = 0.05


@dataclass
class PolicyConfig:
    min_quality: float = 0.60
    max_latency_ms: float = 2500.0
    max_cost_per_query: float = 0.02
    max_quality_drop: float = 0.05
    weights: Weights = field(default_factory=Weights)


@dataclass
class MetricsConfig:
    enabled: list[str]


@dataclass
class CIConfig:
    mode: str = "fail"
    post_pr_comment: bool = True


@dataclass
class PricingConfig:
    input_per_1k: float = 0.001
    output_per_1k: float = 0.002


@dataclass
class AppConfig:
    datasets: DatasetConfig
    candidates: list[CandidateConfig]
    metrics: MetricsConfig
    policy: PolicyConfig
    ci: CIConfig
    pricing: dict[str, PricingConfig]


@dataclass
class DatasetRecord:
    id: str
    question: str
    reference_answer: str
    contexts: list[str]


@dataclass
class CaseMetrics:
    quality: float
    groundedness: float
    citation: float
    latency_ms: float
    cost: float
    score: float
    passed_hard_constraints: bool


@dataclass
class CaseResult:
    record_id: str
    answer: str
    selected_contexts: list[str]
    metrics: CaseMetrics


@dataclass
class CandidateAggregate:
    quality: float
    groundedness: float
    citation: float
    latency_ms: float
    cost: float
    score: float
    passed_hard_constraints: bool


@dataclass
class CandidateResult:
    name: str
    provider: str
    model: str
    aggregate: CandidateAggregate
    cases: list[CaseResult]


@dataclass
class RunResult:
    run_id: str
    generated_at: str
    dataset_path: str
    policy: PolicyConfig
    candidates: list[CandidateResult]


@dataclass
class Recommendation:
    winner: str | None
    reason: str
    ranking: list[str]


@dataclass
class RegressionDelta:
    quality: float
    groundedness: float
    citation: float
    latency_ms: float
    cost: float
    score: float


@dataclass
class RegressionReport:
    baseline_candidate: str
    candidate: str
    deltas: RegressionDelta
    breached: bool
    verdict: str


@dataclass
class GenerationOutput:
    answer: str
    latency_ms: float
    input_tokens: int
    output_tokens: int


def to_dict(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    return obj
