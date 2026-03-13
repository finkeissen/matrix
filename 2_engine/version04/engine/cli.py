"""Command-line interface for the Matrix Engine.

Commands:
  - run <run_dir>      : process a single run directory
  - daemon             : watch RUNS_ROOT/incoming and process runs continuously

Defaults are taken from environment variables so that systemd can supply a
single central config file (see config/matrix-engine.env).
"""

#!/usr/bin/env python3
import argparse
from pathlib import Path
import os
from engine.conductor import daemon_loop, run_single

def main(argv=None):
    p = argparse.ArgumentParser(prog="engine", description="Matrix Engine (local boundary-control runner)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Run pipeline for a single run directory")
    r.add_argument("run_dir", type=Path)

    d = sub.add_parser("daemon", help="Consume incoming runs from RUNS_ROOT")
    d.add_argument("--runs-root", type=Path, default=Path(os.environ.get("MATRIX_RUNS_ROOT", "/home/ef/ram/runs")))
    d.add_argument("--poll-sec", type=float, default=float(os.environ.get("MATRIX_POLL_SEC", "1.0")))

    args = p.parse_args(argv)
    if args.cmd == "run":
        return run_single(args.run_dir)
    if args.cmd == "daemon":
        return daemon_loop(args.runs_root, poll_sec=args.poll_sec)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
