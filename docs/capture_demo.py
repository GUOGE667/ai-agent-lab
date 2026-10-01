"""Capture a fresh scripted offline demo for the static walkthrough page."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path(__file__).with_name("demo_trace.json")


def test_excerpt(output: str) -> str:
    """Keep useful test lines without machine-specific temporary paths."""
    prefixes = ("test_", "AssertionError:", "Ran ", "FAILED", "OK")
    lines = []
    for line in output.splitlines():
        if line.startswith(prefixes):
            lines.append(line.split(" in ", 1)[0] if line.startswith("Ran ") else line)
    return "\n".join(lines)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="issue-agent-page-") as temp:
        run_dir = Path(temp) / "run"
        subprocess.run(
            [sys.executable, "-m", "issue_agent.cli", "demo", "--output", str(run_dir)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
        trace = json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))
        patch = (run_dir / "changes.diff").read_text(encoding="utf-8")

    assert report["execution_mode"] == "scripted_offline_demo"
    assert report["usage"]["total_tokens"] == 0
    assert report["baseline_tests"]["exit_code"] != 0
    assert report["final_tests"]["exit_code"] == 0
    assert [step["tool"] for step in trace] == ["read_file", "replace_text", "run_tests"]
    assert patch
    for step in trace:
        if step["tool"] == "run_tests":
            step["result"]["output"] = test_excerpt(step["result"]["output"])
    data = {
        "execution_mode": report["execution_mode"],
        "issue": (ROOT / "examples/calculator_bug/issue.md").read_text(encoding="utf-8").strip(),
        "baseline": {"exit_code": report["baseline_tests"]["exit_code"],
                     "output": test_excerpt(report["baseline_tests"]["output"])},
        "steps": trace,
        "final": {"exit_code": report["final_tests"]["exit_code"],
                  "output": test_excerpt(report["final_tests"]["output"])},
        "patch": patch,
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Captured scripted offline trace in {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
