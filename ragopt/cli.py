from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from ragopt.config import load_config
from ragopt.engine import compare_runs, load_run, recommend, run_evaluation
from ragopt.github import post_pr_comment
from ragopt.reporting import build_regression_markdown, build_run_markdown, write_report


def cmd_run(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    result = run_evaluation(cfg, artifacts_dir=args.artifacts_dir)
    rec = recommend(result)
    report = build_run_markdown(result, rec)

    run_path = f"{args.artifacts_dir}/run_{result.run_id}.json"
    print(f"Run saved: {run_path}")

    if args.report:
        write_report(args.report, report)
        print(f"Report saved: {args.report}")

    if args.print_json:
        print(json.dumps(asdict(result), indent=2))

    if args.github_pr_comment:
        posted = post_pr_comment(report)
        print(f"PR comment posted: {posted}")

    if cfg.ci.mode == "fail" and rec.winner is None:
        return 1
    return 0


def cmd_recommend(args: argparse.Namespace) -> int:
    run = load_run(args.run)
    rec = recommend(run)
    print(json.dumps(asdict(rec), indent=2))
    return 0 if rec.winner else 1


def cmd_compare(args: argparse.Namespace) -> int:
    baseline = load_run(args.baseline)
    candidate = load_run(args.candidate)
    report = compare_runs(baseline, candidate, args.baseline_name, args.candidate_name)
    md = build_regression_markdown(report)

    if args.report:
        write_report(args.report, md)
        print(f"Regression report saved: {args.report}")

    print(json.dumps(asdict(report), indent=2))
    return 1 if report.breached and args.fail_on_breach else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ragopt", description="RAG optimizer CI tool")
    sp = p.add_subparsers(dest="command", required=True)

    runp = sp.add_parser("run", help="Run evaluation for all candidates")
    runp.add_argument("--config", required=True)
    runp.add_argument("--artifacts-dir", default="artifacts")
    runp.add_argument("--report", default="artifacts/report.md")
    runp.add_argument("--print-json", action="store_true")
    runp.add_argument("--github-pr-comment", action="store_true")
    runp.set_defaults(func=cmd_run)

    recp = sp.add_parser("recommend", help="Recommend best candidate from run json")
    recp.add_argument("--run", required=True)
    recp.set_defaults(func=cmd_recommend)

    compp = sp.add_parser("compare", help="Compare candidate against baseline run")
    compp.add_argument("--baseline", required=True)
    compp.add_argument("--candidate", required=True)
    compp.add_argument("--baseline-name", required=True)
    compp.add_argument("--candidate-name", required=True)
    compp.add_argument("--report", default="artifacts/regression.md")
    compp.add_argument("--fail-on-breach", action="store_true")
    compp.set_defaults(func=cmd_compare)

    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    code = args.func(args)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
