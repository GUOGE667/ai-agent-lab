"""Deterministic outcome classification for run reports."""

from __future__ import annotations

from collections import Counter


def classify_result(row: dict) -> str:
    if row.get("error"):
        return "run_error"
    baseline = row.get("baseline_tests") or {}
    final = row.get("final_tests") or {}
    check = row.get("check")
    if baseline.get("exit_code") is None:
        return "invalid_baseline"
    if baseline.get("exit_code") == 0:
        return "already_passing"
    if not row.get("changed_files"):
        return "no_edit"
    if final.get("timed_out") or (check and check.get("timed_out")):
        return "test_timeout"
    if final.get("exit_code") != 0:
        return "tests_failed"
    if check and check.get("exit_code") != 0:
        return "check_failed"
    return "passed"


def aggregate_results(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("Cannot aggregate an empty task set")
    counts = Counter(classify_result(row) for row in rows)
    total_tokens = sum((row.get("usage") or {}).get("total_tokens", 0) or 0 for row in rows)
    total_seconds = sum(row.get("elapsed_seconds", 0) or 0 for row in rows)
    tool_errors = sum(row.get("tool_error_count", 0) or 0 for row in rows)
    return {
        "tasks": len(rows),
        "passed": counts["passed"],
        "pass_rate": round(counts["passed"] / len(rows), 3),
        "outcomes": dict(sorted(counts.items())),
        "total_tokens": total_tokens,
        "average_tokens_per_task": round(total_tokens / len(rows), 1),
        "elapsed_seconds": round(total_seconds, 2),
        "average_seconds_per_task": round(total_seconds / len(rows), 2),
        "tool_errors": tool_errors,
    }
