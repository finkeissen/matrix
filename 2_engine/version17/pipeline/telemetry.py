"""
telemetry.py — Pipeline measurement instrumentation (Armaturen).

Every LLM call, step execution, and routing decision is measured and recorded.
After run completion, all raw events are aggregated into telemetry_summary.json
which can be queried to understand process behaviour and guide tuning.

Two output files per run:
  runs/<run_id>/telemetry.jsonl         — raw event stream
  runs/<run_id>/telemetry_summary.json  — aggregated metrics

Usage:
    from telemetry import Telemetry
    tel = Telemetry(work_dir, run_id, enabled=True)

    # Measure a step
    with tel.step("01_scope"):
        result = run_step(...)

    # Measure an LLM call
    raw, llm_meta = tel.llm_call(prompt, prompt_hash, model_class, call_fn)

    # Record routing
    tel.record_routing("05_validation", "proceed", {"score": 0.82})

    # Finalize (writes summary)
    tel.finalize()
"""

import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ms(start: float) -> int:
    return int((time.time() - start) * 1000)


class Telemetry:
    """
    Measurement instrumentation for a single pipeline run.
    All writes are append-only to telemetry.jsonl.
    """

    def __init__(self, work_dir: Path, run_id: str, enabled: bool = True):
        self.work_dir  = work_dir
        self.run_id    = run_id
        self.enabled   = enabled
        self._run_dir  = work_dir / run_id
        self._tel_path = self._run_dir / "telemetry.jsonl"
        self._sum_path = self._run_dir / "telemetry_summary.json"
        self._run_start = time.time()

        # In-memory accumulators for fast aggregation
        self._step_durations: dict[str, list[int]]    = {}
        self._llm_calls:      list[dict]              = []
        self._routing_events: list[dict]              = []
        self._content_metrics: list[dict]             = []

    # ── Internal write ────────────────────────────────────────────────────────

    def _write(self, event: dict) -> None:
        if not self.enabled:
            return
        self._run_dir.mkdir(parents=True, exist_ok=True)
        with open(self._tel_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    # ── Step timing ───────────────────────────────────────────────────────────

    @contextmanager
    def step(self, step_name: str):
        """Context manager: measures step wall-clock duration."""
        t0 = time.time()
        try:
            yield
        finally:
            duration_ms = _ms(t0)
            self._step_durations.setdefault(step_name, []).append(duration_ms)
            self._write({
                "ts":          _now(),
                "event":       "step.measured",
                "step":        step_name,
                "duration_ms": duration_ms,
            })

    # ── LLM call measurement ─────────────────────────────────────────────────

    def llm_call(
        self,
        prompt_text: str,
        prompt_hash: str,
        step_name: str,
        model_class: str,
        call_fn: Callable[[str], Optional[str]],
        retries: int = 0,
    ) -> tuple[Optional[str], dict]:
        """
        Wraps an LLM call function with measurement.
        call_fn: callable(prompt_text) → raw_response_str | None

        Returns: (raw_response, llm_meta)
        llm_meta contains all measured properties for use in state.jsonl / run_record.
        """
        if not self.enabled:
            raw = call_fn(prompt_text)
            return raw, {}

        t0         = time.time()
        attempt    = 0
        raw        = None
        success    = False
        last_error = None

        for attempt in range(retries + 1):
            try:
                raw     = call_fn(prompt_text)
                success = raw is not None
                if success:
                    break
            except Exception as e:
                last_error = str(e)

        duration_ms  = _ms(t0)
        tokens_in    = _estimate_tokens(prompt_text)
        tokens_out   = _estimate_tokens(raw) if raw else 0

        llm_meta = {
            "step":          step_name,
            "model_class":   model_class,
            "prompt_hash":   prompt_hash,
            "duration_ms":   duration_ms,
            "tokens_in_est": tokens_in,
            "tokens_out_est": tokens_out,
            "success":       success,
            "attempt_count": attempt + 1,
            "last_error":    last_error,
        }

        self._llm_calls.append(llm_meta)
        self._write({
            "ts":    _now(),
            "event": "llm.call",
            **llm_meta,
        })

        return raw, llm_meta

    # ── JSON parse measurement ────────────────────────────────────────────────

    def record_parse(self, step_name: str, prompt_hash: str,
                     success: bool, errors: list = None) -> None:
        """Record whether LLM response parsed as valid JSON."""
        self._write({
            "ts":          _now(),
            "event":       "llm.parse",
            "step":        step_name,
            "prompt_hash": prompt_hash,
            "success":     success,
            "errors":      errors or [],
        })

    # ── Routing decisions ─────────────────────────────────────────────────────

    def record_routing(self, step_name: str, decision: str,
                       payload: dict = None) -> None:
        """Record a routing decision (proceed/clarify/retry etc.)."""
        event = {
            "ts":       _now(),
            "event":    "routing",
            "step":     step_name,
            "decision": decision,
            **(payload or {}),
        }
        self._routing_events.append(event)
        self._write(event)

    # ── Content quality metrics ───────────────────────────────────────────────

    def record_content(self, step_name: str, metrics: dict) -> None:
        """
        Record content-level quality metrics for a step.
        Examples:
          step_01_scope:      boundaries_count, exclusions_count
          step_04b:           problems_added, problems_removed
          step_05_validation: atomicity_failure_rate, duplicates_count
          step_07_hall:       flagged_count, flagged_rate
        """
        entry = {
            "ts":    _now(),
            "event": "content.metrics",
            "step":  step_name,
            **metrics,
        }
        self._content_metrics.append(entry)
        self._write(entry)

    # ── Novelty Guard events ──────────────────────────────────────────────────

    def record_cache_hit(self, step_name: str, task_id: str) -> None:
        self._write({
            "ts":      _now(),
            "event":   "novelty.cache_hit",
            "step":    step_name,
            "task_id": task_id,
        })

    def record_cache_miss(self, step_name: str, task_id: str) -> None:
        self._write({
            "ts":      _now(),
            "event":   "novelty.cache_miss",
            "step":    step_name,
            "task_id": task_id,
        })

    # ── Stop events ───────────────────────────────────────────────────────────

    def record_stop(self, step_name: str, stop_code: str, reason: str = "") -> None:
        self._write({
            "ts":        _now(),
            "event":     "pipeline.stop",
            "step":      step_name,
            "stop_code": stop_code,
            "reason":    reason,
        })

    # ── Finalization: aggregate summary ──────────────────────────────────────

    def finalize(self) -> dict:
        """
        Aggregate all raw telemetry into telemetry_summary.json.
        Returns the summary dict.
        """
        total_duration_ms = _ms(self._run_start)

        # Step duration summary
        step_summary = {}
        for step, durations in self._step_durations.items():
            step_summary[step] = {
                "calls":          len(durations),
                "total_ms":       sum(durations),
                "avg_ms":         int(sum(durations) / len(durations)),
                "min_ms":         min(durations),
                "max_ms":         max(durations),
            }

        # LLM call summary
        llm_total     = len(self._llm_calls)
        llm_success   = sum(1 for c in self._llm_calls if c.get("success"))
        llm_error_rate = round(1 - llm_success / llm_total, 4) if llm_total else 0.0
        llm_avg_ms    = int(sum(c["duration_ms"] for c in self._llm_calls) / llm_total) if llm_total else 0
        llm_tokens_in  = sum(c.get("tokens_in_est", 0) for c in self._llm_calls)
        llm_tokens_out = sum(c.get("tokens_out_est", 0) for c in self._llm_calls)
        llm_retries    = sum(c.get("attempt_count", 1) - 1 for c in self._llm_calls)

        # Per-step LLM breakdown
        llm_by_step: dict[str, dict] = {}
        for c in self._llm_calls:
            s = c.get("step", "?")
            llm_by_step.setdefault(s, {"calls": 0, "success": 0, "total_ms": 0,
                                       "tokens_in": 0, "tokens_out": 0, "retries": 0})
            llm_by_step[s]["calls"]      += 1
            llm_by_step[s]["success"]    += 1 if c.get("success") else 0
            llm_by_step[s]["total_ms"]   += c.get("duration_ms", 0)
            llm_by_step[s]["tokens_in"]  += c.get("tokens_in_est", 0)
            llm_by_step[s]["tokens_out"] += c.get("tokens_out_est", 0)
            llm_by_step[s]["retries"]    += c.get("attempt_count", 1) - 1

        # Prompt performance (group by prompt_hash)
        prompt_perf: dict[str, dict] = {}
        for c in self._llm_calls:
            ph = c.get("prompt_hash", "unknown")
            st = c.get("step", "?")
            key = f"{st}:{ph[:12]}"
            prompt_perf.setdefault(key, {
                "step": st, "prompt_hash": ph,
                "calls": 0, "success": 0,
            })
            prompt_perf[key]["calls"]   += 1
            prompt_perf[key]["success"] += 1 if c.get("success") else 0

        for v in prompt_perf.values():
            v["success_rate"] = round(v["success"] / v["calls"], 4) if v["calls"] else 0.0

        # Routing summary
        routing_summary: dict[str, dict] = {}
        for r in self._routing_events:
            step = r.get("step", "?")
            dec  = r.get("decision", "?")
            routing_summary.setdefault(step, {})
            routing_summary[step][dec] = routing_summary[step].get(dec, 0) + 1

        # Content metrics aggregation
        content_agg: dict[str, dict] = {}
        for m in self._content_metrics:
            step = m.get("step", "?")
            content_agg.setdefault(step, {})
            for k, v in m.items():
                if k in ("ts", "event", "step"):
                    continue
                if isinstance(v, (int, float)):
                    content_agg[step].setdefault(k, []).append(v)

        # Average numeric content metrics
        content_avg: dict[str, dict] = {}
        for step, metrics in content_agg.items():
            content_avg[step] = {}
            for k, vals in metrics.items():
                content_avg[step][k] = round(sum(vals) / len(vals), 4) if vals else 0

        # Novelty Guard efficiency
        cache_hits   = sum(1 for e in self._read_events() if e.get("event") == "novelty.cache_hit")
        cache_misses = sum(1 for e in self._read_events() if e.get("event") == "novelty.cache_miss")

        summary = {
            "run_id":             self.run_id,
            "finalized_at":       _now(),
            "total_duration_ms":  total_duration_ms,
            "total_duration_s":   round(total_duration_ms / 1000, 1),

            "llm": {
                "total_calls":      llm_total,
                "success_count":    llm_success,
                "error_rate":       llm_error_rate,
                "total_retries":    llm_retries,
                "avg_latency_ms":   llm_avg_ms,
                "total_tokens_in_est":  llm_tokens_in,
                "total_tokens_out_est": llm_tokens_out,
                "by_step":          llm_by_step,
            },

            "steps":              step_summary,
            "routing":            routing_summary,
            "content_metrics":    content_avg,
            "prompt_performance": list(prompt_perf.values()),

            "novelty_guard": {
                "cache_hits":   cache_hits,
                "cache_misses": cache_misses,
                "hit_rate":     round(cache_hits / (cache_hits + cache_misses), 4)
                                if (cache_hits + cache_misses) > 0 else 0.0,
            },
        }

        if self.enabled:
            with open(self._sum_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

        return summary

    def _read_events(self) -> list[dict]:
        """Read all raw events from telemetry.jsonl for aggregation."""
        events = []
        if self._tel_path.exists():
            with open(self._tel_path) as f:
                for line in f:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
        return events


# ── Token estimation ──────────────────────────────────────────────────────────

def _estimate_tokens(text: str) -> int:
    """
    Rough token estimate: ~4 chars per token (OpenAI approximation).
    Not accurate — used only for telemetry, not billing.
    """
    if not text:
        return 0
    return max(1, len(text) // 4)
