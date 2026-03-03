# Architecture

## Flow

1. Load `ragopt.yaml`.
2. Load benchmark dataset.
3. For each candidate:
   - run generation over each query
   - compute per-case metrics
   - aggregate metrics
   - apply hard constraints
4. Rank candidates by weighted score.
5. Persist JSON artifact + markdown report.
6. Optionally post markdown to GitHub PR.
7. UI loads run artifact JSON for interactive inspection.

## Modules

- `ragopt/models.py`: schema and result types
- `ragopt/config.py`: config and dataset loading
- `ragopt/adapters.py`: generation provider abstraction
- `ragopt/metrics.py`: metric and scoring functions
- `ragopt/engine.py`: orchestration and comparison
- `ragopt/reporting.py`: markdown outputs
- `ragopt/github.py`: PR comment helper
- `ragopt/cli.py`: public command interface
- `ui/`: React + TypeScript dashboard for viewing run artifacts

## Extension points

- Add providers in `adapters.py`.
- Add new metrics in `metrics.py` and wire into engine.
- Add policy checks in `engine.py` compare/run paths.
- Connect `ui/` to a live backend API instead of file upload only.
