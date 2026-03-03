from __future__ import annotations

import re
from collections import Counter


TOKEN_RE = re.compile(r"[A-Za-z0-9']+")
CIT_RE = re.compile(r"\[(\d+)\]")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def overlap_f1(pred: str, ref: str) -> float:
    p = tokenize(pred)
    r = tokenize(ref)
    if not p or not r:
        return 0.0
    pc = Counter(p)
    rc = Counter(r)
    common = sum((pc & rc).values())
    precision = common / len(p)
    recall = common / len(r)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def groundedness(answer: str, contexts: list[str]) -> float:
    a = tokenize(answer)
    if not a:
        return 0.0
    cset = set(tokenize(" ".join(contexts)))
    hits = sum(1 for tok in a if tok in cset)
    return hits / len(a)


def citation_hit_rate(answer: str, contexts: list[str]) -> float:
    refs = [int(m.group(1)) for m in CIT_RE.finditer(answer)]
    if not refs:
        return 0.0
    valid = 0
    for idx in refs:
        if 1 <= idx <= len(contexts):
            valid += 1
    return valid / len(refs)


def estimate_cost(input_tokens: int, output_tokens: int, input_per_1k: float, output_per_1k: float) -> float:
    return (input_tokens / 1000.0) * input_per_1k + (output_tokens / 1000.0) * output_per_1k


def overall_score(
    quality: float,
    groundedness_score: float,
    citation: float,
    latency_ms: float,
    cost: float,
    max_latency_ms: float,
    max_cost: float,
    w_quality: float,
    w_groundedness: float,
    w_citation: float,
    w_latency: float,
    w_cost: float,
) -> float:
    latency_norm = min(latency_ms / max_latency_ms, 1.0)
    cost_norm = min(cost / max_cost, 1.0)
    return (
        w_quality * quality
        + w_groundedness * groundedness_score
        + w_citation * citation
        - w_latency * latency_norm
        - w_cost * cost_norm
    )
