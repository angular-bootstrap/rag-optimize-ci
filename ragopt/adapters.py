from __future__ import annotations

import json
import os
import random
import time
import urllib.request
from abc import ABC, abstractmethod
from time import perf_counter

from ragopt.models import GenerationOutput


class BaseAdapter(ABC):
    @abstractmethod
    def generate(self, question: str, contexts: list[str], prompt_template: str, model: str, params: dict) -> GenerationOutput:
        raise NotImplementedError


class MockAdapter(BaseAdapter):
    """Deterministic adapter for local reproducible runs."""

    def generate(self, question: str, contexts: list[str], prompt_template: str, model: str, params: dict) -> GenerationOutput:
        seed = params.get("seed", 42)
        rnd = random.Random(f"{seed}:{model}:{question}")

        top_context = contexts[0] if contexts else ""
        style = params.get("style", "brief")
        if style == "detailed":
            answer = f"{top_context} Therefore: {question} [1]"
        else:
            answer = f"{top_context[:220]} [1]"

        latency_ms = rnd.uniform(120, 450)
        time.sleep(0.001)

        input_tokens = max(1, len((question + " " + " ".join(contexts)).split()))
        output_tokens = max(1, len(answer.split()))
        return GenerationOutput(answer=answer, latency_ms=latency_ms, input_tokens=input_tokens, output_tokens=output_tokens)


class OpenAIAdapter(BaseAdapter):
    def generate(self, question: str, contexts: list[str], prompt_template: str, model: str, params: dict) -> GenerationOutput:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required for provider=openai")

        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        url = f"{base_url}/chat/completions"

        user_prompt = _build_user_prompt(question, contexts, prompt_template)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You answer questions using provided context and cite sources as [n]."},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": params.get("temperature", 0),
            "max_tokens": params.get("max_tokens", 250),
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        started = perf_counter()
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8"))
        latency_ms = (perf_counter() - started) * 1000

        answer = body["choices"][0]["message"]["content"]
        usage = body.get("usage", {})
        in_tokens = int(usage.get("prompt_tokens", max(1, len(user_prompt.split()))))
        out_tokens = int(usage.get("completion_tokens", max(1, len(answer.split()))))
        return GenerationOutput(answer=answer, latency_ms=latency_ms, input_tokens=in_tokens, output_tokens=out_tokens)


class OllamaAdapter(BaseAdapter):
    def generate(self, question: str, contexts: list[str], prompt_template: str, model: str, params: dict) -> GenerationOutput:
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        url = f"{base_url}/api/generate"

        user_prompt = _build_user_prompt(question, contexts, prompt_template)
        payload = {
            "model": model,
            "prompt": user_prompt,
            "stream": False,
            "options": params.get("options", {}),
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        started = perf_counter()
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8"))
        latency_ms = (perf_counter() - started) * 1000

        answer = body.get("response", "")
        prompt_eval_count = int(body.get("prompt_eval_count", max(1, len(user_prompt.split()))))
        eval_count = int(body.get("eval_count", max(1, len(answer.split()))))
        return GenerationOutput(answer=answer, latency_ms=latency_ms, input_tokens=prompt_eval_count, output_tokens=eval_count)


class LocalHTTPAdapter(BaseAdapter):
    """Adapter for custom local inference service.

    Expects POST endpoint from env RAGOPT_LOCAL_ENDPOINT, with JSON body:
    {question, contexts, prompt_template, model, params}

    Response JSON:
    {answer, latency_ms?, input_tokens?, output_tokens?}
    """

    def generate(self, question: str, contexts: list[str], prompt_template: str, model: str, params: dict) -> GenerationOutput:
        endpoint = os.getenv("RAGOPT_LOCAL_ENDPOINT")
        if not endpoint:
            raise RuntimeError("RAGOPT_LOCAL_ENDPOINT is required for provider=local-http")

        payload = {
            "question": question,
            "contexts": contexts,
            "prompt_template": prompt_template,
            "model": model,
            "params": params,
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        started = perf_counter()
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
            body = json.loads(resp.read().decode("utf-8"))
        fallback_latency = (perf_counter() - started) * 1000

        answer = body.get("answer", "")
        latency_ms = float(body.get("latency_ms", fallback_latency))
        input_tokens = int(body.get("input_tokens", max(1, len((question + ' ' + ' '.join(contexts)).split()))))
        output_tokens = int(body.get("output_tokens", max(1, len(answer.split()))))
        return GenerationOutput(answer=answer, latency_ms=latency_ms, input_tokens=input_tokens, output_tokens=output_tokens)


def _build_user_prompt(question: str, contexts: list[str], prompt_template: str) -> str:
    numbered_context = "\n".join(f"[{i}] {c}" for i, c in enumerate(contexts, start=1))
    prompt = prompt_template.replace("{question}", question)
    return f"Context:\n{numbered_context}\n\nInstruction:\n{prompt}"


def get_adapter(provider: str) -> BaseAdapter:
    if provider == "mock":
        return MockAdapter()
    if provider == "openai":
        return OpenAIAdapter()
    if provider == "ollama":
        return OllamaAdapter()
    if provider in {"local-http", "local_http"}:
        return LocalHTTPAdapter()
    raise ValueError(f"Unsupported provider '{provider}'. Supported: mock, openai, ollama, local-http")
