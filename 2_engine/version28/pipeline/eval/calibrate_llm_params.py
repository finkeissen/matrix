from __future__ import annotations

import argparse
import itertools
from pathlib import Path

from .io_utils import load_json, write_json
from .parameter_spaces import STEP_SEARCH_SPACES, SUITABILITY_THRESHOLDS
from .runner import execute_pipeline_run
from .scoring import score_step


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calibrate LLM parameters for a specific step.")
    parser.add_argument("--domain", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--step", required=True)
    parser.add_argument("--run-cmd", required=True, help='Example: "python -m pipeline.cli run --domain {domain}"')
    parser.add_argument("--runs-dir", default="data/runs")
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--max-trials", type=int, default=12)
    parser.add_argument("--out-dir", default="pipeline/eval/reports")
    parser.add_argument("--profiles-path", default="pipeline/eval/profiles/calibrated_profiles.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runs_dir = Path(args.runs_dir)
    cwd = Path(args.cwd)
    out_dir = Path(args.out_dir)
    profiles_path = Path(args.profiles_path)

    space = STEP_SEARCH_SPACES.get(args.step)
    if not space:
        raise SystemExit(f"No search space defined for step: {args.step}")

    combos = list(itertools.product(space["temperature"], space["top_p"], space["max_tokens"]))
    combos = combos[: args.max_trials]

    trials = []
    best = None

    for temperature, top_p, max_tokens in combos:
        env = {
            "LLM_MODEL": args.model,
            "LLM_EVAL_STEP": args.step,
            "LLM_TEMPERATURE": str(temperature),
            "LLM_TOP_P": str(top_p),
            "LLM_MAX_TOKENS": str(max_tokens),
        }

        result = execute_pipeline_run(
            domain=args.domain,
            run_cmd_template=args.run_cmd,
            runs_dir=runs_dir,
            extra_env=env,
            cwd=cwd,
            timeout=args.timeout,
        )

        score = score_step(args.step, result.metrics, result.run_health)

        trial = {
            "params": {
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
            },
            "returncode": result.returncode,
            "run_dir": result.run_dir,
            "score": score,
            "metrics": result.metrics,
            "run_health": result.run_health,
        }
        trials.append(trial)

        if best is None or score > best["score"]:
            best = trial

    threshold = SUITABILITY_THRESHOLDS.get(args.step, 0.6)
    suitable = best is not None and best["score"] >= threshold

    report = {
        "model": args.model,
        "domain": args.domain,
        "step": args.step,
        "suitable": suitable,
        "threshold": threshold,
        "best_trial": best,
        "trials": trials,
    }

    out_path = out_dir / f"calibration_{args.model}_{args.step}_{args.domain}.json"
    write_json(out_path, report)

    calibrated_profiles = load_json(profiles_path) if profiles_path.exists() else {}
    if best and suitable:
        calibrated_profiles.setdefault(args.model, {})
        calibrated_profiles[args.model][args.step] = best["params"]
        write_json(profiles_path, calibrated_profiles)

    print(f"Calibration report written to: {out_path}")
    if best:
        print(f"Best params: {best['params']} | score={best['score']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
