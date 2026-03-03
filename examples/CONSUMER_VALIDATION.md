# Consumer Validation

This file records a separate-repo validation run.

## Environment

- Consumer path: `/tmp/ragopt-consumer`
- Tool path: `/Users/harmeetsingh/Documents/app/AI-Project`
- Command:

```bash
cd /tmp/ragopt-consumer
PYTHONPATH=/Users/harmeetsingh/Documents/app/AI-Project python3 -m ragopt.cli run --config ragopt.yaml --report artifacts/report.md
```

## Result

- `artifacts/run_75b0502b.json` generated
- `artifacts/report.md` generated
- Exit code: `0`

## Notes

A direct `pip install` style validation was blocked in this sandbox by network and user-site permission restrictions. GitHub Actions cloud runners are expected to run installation normally.
