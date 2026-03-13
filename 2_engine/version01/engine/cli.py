#!/usr/bin/env python3
import argparse
from pathlib import Path
from engine.conductor import daemon_loop, run_single

def main(argv=None):
    p = argparse.ArgumentParser(prog="engine", description="Matrix Engine (local pipeline)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Run pipeline for a single run directory")
    r.add_argument("run_dir", type=Path)

    d = sub.add_parser("daemon", help="Consume incoming runs from RUNS_ROOT")
    d.add_argument("--runs-root", type=Path, default=Path("/home/ef/ram/runs"))
    d.add_argument("--poll-sec", type=float, default=1.0)

    args = p.parse_args(argv)
    if args.cmd == "run":
        return run_single(args.run_dir)
    if args.cmd == "daemon":
        return daemon_loop(args.runs_root, poll_sec=args.poll_sec)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
