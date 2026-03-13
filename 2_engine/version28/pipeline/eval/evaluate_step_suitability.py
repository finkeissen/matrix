from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from .io_utils import write_json
from .parameter_spaces import STEP_BASELINES, SUITABILITY_THRESHOLDS
from .runner import execute_pipeline_run
from .scoring import score_step, summarize_unsuitability


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate whether a model is suitable for specific pipeline steps.")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--steps", nargs="+", required=True)
    parser.add_argument("--run-cmd", required=True, help='Example: "python -m pipeline.cli run --domain {domain}"')
    parser.add_argument("--runs-dir", default="data/runs")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--out-dir", default="pipeline/eval/reports")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runs_dir = Path(args.runs_dir)
    cwd = Path(args.cwd)
    out_dir = Path(args.out_dir)

    report: dict[str, object] = {
        "model": args.model,
        "domain": args.domain,
        "evaluated_steps": {},
    }

    for step in args.steps:
        baselines = STEP_BASELINES.get(step)
        if not baselines:
            report["evaluated_steps"][step] = {
                "suitable": False,
                "score": 0.0,
                "reason": "no_baselines_defined_for_step",
            }
            continue

        best = None
        trials = []

        for profile in baselines:
            env = {
                "LLM_MODEL": args.model,
                "LLM_EVAL_STEP": step,
                "LLM_TEMPERATURE": str(profile.temperature),
                "LLM_TOP_P": str(profile.top_p),
            }
            if profile.max_tokens is not None:
                env["LLM_MAX_TOKENS"] = str(profile.max_tokens)

            result = execute_pipeline_run(
                domain=args.domain,
                run_cmd_template=args.run_cmd,
                runs_dir=runs_dir,
                extra_env=env,
                cwd=cwd,
                timeout=args.timeout,
            )

            score = score_step(step, result.metrics, result.run_health)
            trial = {
                "profile": asdict(profile),
                "returncode": result.returncode,
                "run_dir": result.run_dir,
                "score": score,
                "metrics": result.metrics,
                "run_health": result.run_health,
            }
            trials.append(trial)

            if best is None or score > best["score"]:
                best = trial

        threshold = SUITABILITY_THRESHOLDS.get(step, 0.6)
        suitable = best is not None and best["score"] >= threshold
        reason = (
            "baseline_profile_passed_threshold"
            if suitable
            else summarize_unsuitability(step, best["score"] if best else 0.0, best["metrics"] if best else {}, best["run_health"] if best else {})
        )

        report["evaluated_steps"][step] = {
            "suitable": suitable,
            "threshold": threshold,
            "best_trial": best,
            "trials": trials,
            "reason": reason,
        }

    out_path = out_dir / f"suitability_{args.model}_{args.domain}.json"
    write_json(out_path, report)
    print(f"Suitability report written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
