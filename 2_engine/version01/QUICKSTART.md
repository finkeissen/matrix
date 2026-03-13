# Quickstart (v0.1.0)

## Create a run
Copy the template into the runtime incoming folder:

  cp -a examples/run-template /home/ef/ram/runs/incoming/run-$(date +%Y%m%d-%H%M%S)

## Run once (manual)
  python3 engine/cli.py run /home/ef/ram/runs/incoming/<run-id>

## Run as daemon
  python3 engine/cli.py daemon --runs-root /home/ef/ram/runs

## Archive finished runs to artifacts
  RUNS_ROOT=/home/ef/ram/runs ARCHIVE_ROOT="/home/ef/Beruflich/GitHub/3.matrix (artifacts)/2.runs" ./scripts/archive_runs.sh
