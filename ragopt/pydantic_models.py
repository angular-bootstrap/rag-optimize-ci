from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class DatasetConfigModel(BaseModel):
    path: str
    sample_size: int | None = None


class CandidateConfigModel(BaseModel):
    name: str
    provider: str = "mock"
    model: str
    prompt_template: str = "Answer using context. Question: {question}"
    retriever_top_k: int = 3
    chunking_strategy: str = "fixed"
    params: dict[str, Any] = Field(default_factory=dict)


class WeightsModel(BaseModel):
    quality: float = 0.45
    groundedness: float = 0.25
    citation: float = 0.15
    latency: float = 0.10
    cost: float = 0.05

    @model_validator(mode="after")
    def non_negative(self) -> "WeightsModel":
        vals = [self.quality, self.groundedness, self.citation, self.latency, self.cost]
        if any(v < 0 for v in vals):
            raise ValueError("weights must be non-negative")
        if sum(vals) <= 0:
            raise ValueError("at least one weight must be > 0")
        return self


class PolicyConfigModel(BaseModel):
    min_quality: float = 0.60
    max_latency_ms: float = 2500.0
    max_cost_per_query: float = 0.02
    max_quality_drop: float = 0.05
    weights: WeightsModel = Field(default_factory=WeightsModel)

    @model_validator(mode="after")
    def valid_ranges(self) -> "PolicyConfigModel":
        if not (0 <= self.min_quality <= 1):
            raise ValueError("policy.min_quality must be in [0,1]")
        if self.max_latency_ms <= 0:
            raise ValueError("policy.max_latency_ms must be > 0")
        if self.max_cost_per_query <= 0:
            raise ValueError("policy.max_cost_per_query must be > 0")
        if self.max_quality_drop < 0:
            raise ValueError("policy.max_quality_drop must be >= 0")
        return self


class MetricsConfigModel(BaseModel):
    enabled: list[str] = Field(default_factory=lambda: ["quality", "groundedness", "citation", "latency", "cost"])


class CIConfigModel(BaseModel):
    mode: str = "fail"
    post_pr_comment: bool = True

    @field_validator("mode")
    @classmethod
    def mode_valid(cls, v: str) -> str:
        if v not in {"fail", "warn"}:
            raise ValueError("ci.mode must be 'fail' or 'warn'")
        return v


class PricingConfigModel(BaseModel):
    input_per_1k: float = 0.001
    output_per_1k: float = 0.002


class AppConfigModel(BaseModel):
    datasets: DatasetConfigModel
    candidates: list[CandidateConfigModel]
    metrics: MetricsConfigModel = Field(default_factory=MetricsConfigModel)
    policy: PolicyConfigModel = Field(default_factory=PolicyConfigModel)
    ci: CIConfigModel = Field(default_factory=CIConfigModel)
    pricing: dict[str, PricingConfigModel] = Field(default_factory=dict)

    @model_validator(mode="after")
    def ensure_candidates(self) -> "AppConfigModel":
        if not self.candidates:
            raise ValueError("At least one candidate is required")
        names = [c.name for c in self.candidates]
        if len(names) != len(set(names)):
            raise ValueError("candidate names must be unique")
        return self


def validate_and_normalize(raw: dict[str, Any]) -> dict[str, Any]:
    model = AppConfigModel.model_validate(raw)
    return model.model_dump()
