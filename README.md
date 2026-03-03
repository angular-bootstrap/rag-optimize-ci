# rag-optimize-ci

`rag-optimize-ci` is a CI-first optimizer for RAG QA systems.

It evaluates candidate RAG configurations, scores quality + groundedness + citation + latency + cost, recommends the best candidate, and can fail CI when constraints or regression policies are breached.

## Explain it simply

If you need to explain this project in plain language:

`rag-optimize-ci` is a quality gate for AI apps that use RAG.  
Before a team merges a change (new prompt/model/retriever settings), this tool tests options on benchmark questions and answers:

- Which option gives better answer quality?
- Is it still grounded in source docs?
- Is it too slow?
- Is it too expensive?

Then it recommends the best option and can block risky changes in PRs.

### Simple example

A startup has a support chatbot and tries a new model to improve answers.

- New model is faster, but answer quality drops.
- `rag-optimize-ci` catches the drop in CI.
- PR gets a scorecard comment.
- Team keeps the safer config instead of shipping a regression.

### 30-second interview pitch

\"I built a CI-first tool for RAG apps that prevents bad AI releases.  
It runs benchmark Q&A tests across candidate configs, scores quality, groundedness, latency, and cost, then recommends the best config and blocks regressions in pull requests.\"

## Why this project

Most eval tools are broad. This project is intentionally opinionated:

- RAG QA only
- GitHub Action first
- Cost-quality-latency optimization for shipping decisions

## Quickstart

### 1. Run sample locally (no install required)

```bash
python3 -m ragopt.cli run --config examples/ragopt.yaml --report artifacts/report.md
```

### 2. Recommend from run artifact

```bash
python3 -m ragopt.cli recommend --run artifacts/run_<RUN_ID>.json
```

### 3. Compare two runs

```bash
python3 -m ragopt.cli compare \
  --baseline artifacts/run_<BASELINE>.json \
  --candidate artifacts/run_<CANDIDATE>.json \
  --baseline-name baseline-lite \
  --candidate-name candidate-detailed \
  --fail-on-breach
```

## Demo PR report

Real generated report from this project:
- [`examples/demo_pr_comment.md`](examples/demo_pr_comment.md)

You can attach a screenshot of this markdown rendered in your PR as `docs/pr-demo.png` and link it in the README after your first public run.

## Consumer repo validation

Validated from a separate repo directory (`/tmp/ragopt-consumer`) with independent config/dataset using source import:

```bash
cd /tmp/ragopt-consumer
PYTHONPATH=/path/to/rag-optimize-ci python3 -m ragopt.cli run --config ragopt.yaml --report artifacts/report.md
```

This produced `artifacts/run_*.json` and `artifacts/report.md` successfully.

## Config parsing and validation

- Offline mode (default): parses JSON syntax in `.yaml` file (JSON is valid YAML).
- Full mode (recommended when dependencies are available):

```bash
pip install '.[full]'
```

With full mode installed:
- true YAML parsing via `PyYAML`
- strict schema validation/defaults via `pydantic`

See:
- [`examples/ragopt.yaml`](examples/ragopt.yaml)
- [`examples/ragopt.true.yaml`](examples/ragopt.true.yaml)

## Provider support

- `mock` (default): deterministic local testing
- `openai`: real API calls via `OPENAI_API_KEY` (`OPENAI_BASE_URL` optional)
- `ollama`: local inference via `OLLAMA_BASE_URL` (default `http://localhost:11434`)
- `local-http`: custom local endpoint via `RAGOPT_LOCAL_ENDPOINT`

## Score formula

```text
overall_score = w1*quality + w2*groundedness + w3*citation - w4*latency_norm - w5*cost_norm
```

Hard constraints are applied first:

- quality >= `min_quality`
- latency <= `max_latency_ms`
- cost/query <= `max_cost_per_query`

## GitHub Action usage

```yaml
name: RAG Optimize
on: [pull_request]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: yourname/rag-optimize-ci@v1
        with:
          config: examples/ragopt.yaml
          report_path: artifacts/report.md
          post_pr_comment: true
```

## CLI

- `ragopt run --config <path> [--report <path>] [--github-pr-comment]`
- `ragopt recommend --run <run_json>`
- `ragopt compare --baseline <run_json> --candidate <run_json> --baseline-name <name> --candidate-name <name> [--fail-on-breach]`

## TypeScript UI

A React + TypeScript dashboard is included in [`ui/`](ui).

```bash
cd ui
npm install
npm run dev
```

Upload any `artifacts/run_*.json` or load the bundled sample.

## Development

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```
