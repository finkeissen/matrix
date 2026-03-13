# Quickstart (v0.2.0)

## Create a run
  cp -a examples/run-template /home/ef/ram/runs/incoming/run-$(date +%Y%m%d-%H%M%S)

Edit:
- README.md (purpose/scope/non-goals/roles/constraints)
- stress_test.md (transfer + counterfactual)
- job.json (cmd)

## Run once
  python3 engine/cli.py run /home/ef/ram/runs/incoming/<run-id>

## Run as daemon
  python3 engine/cli.py daemon --runs-root /home/ef/ram/runs

## Archive append-only
  RUNS_ROOT=/home/ef/ram/runs ARCHIVE_ROOT="/home/ef/Beruflich/GitHub/3.matrix (artifacts)/2.runs" ./scripts/archive_runs_append_only.sh
