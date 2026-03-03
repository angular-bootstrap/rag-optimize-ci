# Contributing

## Setup

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

UI development:

```bash
cd ui
npm install
npm run dev
```

## Development workflow

1. Open an issue describing the bug/feature.
2. Add or update tests first where possible.
3. Keep PRs focused and small.
4. Ensure tests pass before opening PR.

## Good first issues

- Add real YAML parser support.
- Add OpenAI adapter behind env vars.
- Add richer citation matching (semantic not index-only).
- Add configurable latency percentile scoring.

## Code style

- Type hints for public functions.
- Keep functions small and deterministic.
- Add comments only where logic is non-obvious.
