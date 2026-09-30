"""Command-line entry point for running and evaluating issue fixes."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .agent import RunResult, load_key, run_issue
from .evaluation import aggregate_results, classify_result
from .workspace import Workspace


def _command(value: str) -> list[str]:
    try:
        result = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError("Command must be a JSON array of strings") from exc
    if not isinstance(result, list) or not result or any(not isinstance(part, str) or not part for part in result):
        raise argparse.ArgumentTypeError("Command must be a nonempty JSON array of strings")
    return result


def _save(result: RunResult, source: Path, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    (output / "report.json").write_text(json.dumps(result.metadata(), ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "trace.json").write_text(json.dumps(result.trace, ensure_ascii=False, indent=2), encoding="utf-8")
    patch_lines: list[str] = []
    for relative, new_text in result.changed_files.items():
        original = source / relative
        old_text = original.read_text(encoding="utf-8") if original.exists() else ""
        patch_lines.extend(difflib.unified_diff(
            old_text.splitlines(keepends=True), new_text.splitlines(keepends=True),
            fromfile=f"a/{relative}" if original.exists() else "/dev/null",
            tofile=f"b/{relative}",
        ))
    (output / "changes.diff").write_text("".join(patch_lines), encoding="utf-8")


def _run_one(repo: Path, issue: str, test_command: list[str], model: str, key: str, max_steps: int, check_command: list[str] | None = None) -> tuple[RunResult, dict | None]:
    with Workspace(repo, test_command) as workspace:
        result = run_issue(workspace, issue, model, key, max_steps=max_steps)
        check = workspace.run_tests(check_command) if check_command and result.changed_files else None
        return result, check


def _load_tasks(tasks_path: Path) -> list[dict]:
    tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Task file must contain a nonempty JSON array")
    seen = set()
    for index, task in enumerate(tasks, 1):
        if not isinstance(task, dict):
            raise ValueError(f"Task {index} must be an object")
        if not isinstance(task.get("id"), str) or not task["id"].strip() or task["id"] in seen:
            raise ValueError(f"Task {index} needs a unique nonempty id")
        seen.add(task["id"])
        if not isinstance(task.get("repo"), str) or not task["repo"].strip():
            raise ValueError(f"Task {index} needs a repo path")
        if not isinstance(task.get("issue"), str) or not task["issue"].strip():
            raise ValueError(f"Task {index} needs an issue")
        for field in ("test_command", "check_command"):
            command = task.get(field)
            if field == "check_command" and command is None:
                continue
            if not isinstance(command, list) or not command or any(not isinstance(part, str) or not part for part in command):
                raise ValueError(f"Task {index} needs a nonempty {field} array")
    return tasks


def _check_command(task: dict, tasks_path: Path) -> list[str] | None:
    command = task.get("check_command")
    if command is None:
        return None
    return [part.replace("{tasks_dir}", str(tasks_path.parent)) for part in command]


def _scripted_demo(payload: dict, _key: str) -> dict:
    """Deterministic example responses; never connects to a model service."""
    previous = payload.get("previous_response_id")
    if previous is None:
        return {"id": "demo-1", "output": [{"type": "function_call", "call_id": "demo-call-1", "name": "read_file", "arguments": '{"path":"calculator.py"}'}]}
    if previous == "demo-1":
        return {"id": "demo-2", "output": [{"type": "function_call", "call_id": "demo-call-2", "name": "replace_text", "arguments": '{"path":"calculator.py","old":"return a - b","new":"return a + b"}'}]}
    if previous == "demo-2":
        return {"id": "demo-3", "output": [{"type": "function_call", "call_id": "demo-call-3", "name": "run_tests", "arguments": "{}"}]}
    return {"id": "demo-4", "output": [{"type": "message", "content": [{"type": "output_text", "text": "Scripted offline demo: fixed add and ran tests."}]}]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fix small repository issues in a temporary copy")
    sub = parser.add_subparsers(dest="mode", required=True)
    demo = sub.add_parser("demo", help="Run a scripted offline demonstration; no API usage")
    demo.add_argument("--output", type=Path)
    check = sub.add_parser("check", help="Validate task definitions and baseline tests offline")
    check.add_argument("--tasks", type=Path, required=True)
    analyze = sub.add_parser("analyze", help="Summarize saved run reports offline; no API usage")
    analyze.add_argument("reports", type=Path, nargs="+", help="Run directories or report.json files")
    analyze.add_argument("--include-demo", action="store_true", help="Include scripted demos in learning-only summaries")
    analyze.add_argument("--output", type=Path)
    run = sub.add_parser("run", help="Run one issue with a model; requires --live")
    run.add_argument("--repo", type=Path, required=True)
    run.add_argument("--issue-file", type=Path, required=True)
    run.add_argument("--test-command", type=_command, required=True, help='JSON array, e.g. ["python","-m","unittest"]')
    run.add_argument("--model", default="gpt-5.1")
    run.add_argument("--max-steps", type=int, default=20)
    run.add_argument("--output", type=Path)
    run.add_argument("--live", action="store_true", help="Explicitly allow paid OpenAI API calls")
    evaluate = sub.add_parser("eval", help="Run a JSON task set with a model; requires --live")
    evaluate.add_argument("--tasks", type=Path, required=True)
    evaluate.add_argument("--model", default="gpt-5.1")
    evaluate.add_argument("--max-steps", type=int, default=20)
    evaluate.add_argument("--output", type=Path)
    evaluate.add_argument("--live", action="store_true", help="Explicitly allow paid OpenAI API calls")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        if args.mode == "demo":
            repo = root / "examples" / "calculator_bug"
            issue = (repo / "issue.md").read_text(encoding="utf-8")
            with Workspace(repo, ["{python}", "-m", "unittest", "discover", "-v"]) as workspace:
                result = run_issue(workspace, issue, "scripted-offline", "", max_steps=8, request_fn=_scripted_demo)
            output = args.output or root / ".runs" / f"demo-{stamp}"
            _save(result, repo, output)
            report = output / "report.json"
            metadata = json.loads(report.read_text(encoding="utf-8"))
            metadata["execution_mode"] = "scripted_offline_demo"
            report.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"execution_mode": "scripted_offline_demo", "tests_passed": result.final_tests["exit_code"] == 0, "output": str(output)}, ensure_ascii=False, indent=2))
            return 0 if result.final_tests["exit_code"] == 0 else 1
        if args.mode == "check":
            tasks_path = args.tasks.expanduser().resolve(strict=True)
            tasks = _load_tasks(tasks_path)
            rows = []
            for task in tasks:
                repo = (tasks_path.parent / task["repo"]).resolve(strict=True)
                with Workspace(repo, task["test_command"]) as workspace:
                    baseline = workspace.run_tests()
                    command = _check_command(task, tasks_path)
                    acceptance = workspace.run_tests(command) if command else None
                valid = baseline["exit_code"] not in (None, 0)
                acceptance_valid = acceptance is None or acceptance["exit_code"] not in (None, 0)
                rows.append({"id": task["id"], "baseline_fails": valid, "exit_code": baseline["exit_code"],
                             "acceptance_baseline_fails": acceptance_valid, "check_exit_code": acceptance["exit_code"] if acceptance else None})
            print(json.dumps({"mode": "offline_check", "tasks": rows}, ensure_ascii=False, indent=2))
            return 0 if all(row["baseline_fails"] and row["acceptance_baseline_fails"] for row in rows) else 1
        if args.mode == "analyze":
            rows = []
            skipped = 0
            included_demo = 0
            for report_path in args.reports:
                report_path = report_path.expanduser().resolve(strict=True)
                if report_path.is_dir():
                    report_path = report_path / "report.json"
                report = json.loads(report_path.read_text(encoding="utf-8"))
                if report.get("execution_mode") == "scripted_offline_demo" and not args.include_demo:
                    skipped += 1
                    continue
                if report.get("execution_mode") == "scripted_offline_demo":
                    included_demo += 1
                row = {"id": report_path.parent.name, **report}
                row["outcome"] = classify_result(row)
                rows.append(row)
            if not rows:
                raise ValueError("No eligible reports; scripted demos require --include-demo")
            summary = {
                "mode": "offline_analysis",
                "skipped_demo_reports": skipped,
                "included_demo_reports": included_demo,
                "valid_for_model_effectiveness": included_demo == 0,
                **aggregate_results(rows),
                "results": rows,
            }
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({key: value for key, value in summary.items() if key != "results"}, ensure_ascii=False, indent=2))
            return 0
        if not args.live:
            raise ValueError("Live API calls are disabled. Add --live only when you intend to use paid API quota")
        key = load_key(root / ".env.local")
        if args.mode == "run":
            repo = args.repo.expanduser().resolve(strict=True)
            issue = args.issue_file.read_text(encoding="utf-8")
            result, _ = _run_one(repo, issue, args.test_command, args.model, key, args.max_steps)
            output = args.output or root / ".runs" / stamp
            _save(result, repo, output)
            print(json.dumps({**result.metadata(), "output": str(output)}, ensure_ascii=False, indent=2))
            return 0 if classify_result(result.metadata()) == "passed" else 1

        tasks_path = args.tasks.expanduser().resolve(strict=True)
        tasks = _load_tasks(tasks_path)
        output = args.output or root / ".runs" / f"eval-{stamp}"
        output.mkdir(parents=True, exist_ok=False)
        rows = []
        for index, task in enumerate(tasks, 1):
            task_id = task.get("id", str(index))
            try:
                repo = (tasks_path.parent / task["repo"]).resolve(strict=True)
                result, check = _run_one(repo, task["issue"], task["test_command"], args.model, key, args.max_steps, _check_command(task, tasks_path))
                task_output = output / f"task-{index:03d}"
                _save(result, repo, task_output)
                row = {"id": task_id, "check": check, **result.metadata()}
                row["outcome"] = classify_result(row)
                row["passed"] = row["outcome"] == "passed"
                rows.append(row)
            except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
                rows.append({"id": task_id, "passed": False, "outcome": "run_error", "error": str(exc), "usage": {"total_tokens": 0}, "elapsed_seconds": 0})
            print(f"{task_id}: {rows[-1]['outcome']}")
        aggregate = {**aggregate_results(rows), "results": rows}
        (output / "evaluation.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({key: value for key, value in aggregate.items() if key != "results"}, ensure_ascii=False, indent=2))
        return 0 if aggregate["passed"] == aggregate["tasks"] else 1
    except (OSError, ValueError, RuntimeError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
