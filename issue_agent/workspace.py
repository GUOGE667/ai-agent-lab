"""Repository copy and narrowly scoped tools exposed to the model."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MAX_FILE_BYTES = 100_000
MAX_OUTPUT_CHARS = 12_000
MAX_CHANGED_FILES = 5
MAX_EDIT_OPERATIONS = 20
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".runs"}
IGNORED_FILES = {".env", ".env.local"}
ALLOWED_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".txt", ".toml", ".yaml", ".yml"}
SAFE_ENV_NAMES = {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR", "HOME", "USERPROFILE", "PYTHONPATH", "VIRTUAL_ENV"}


def _ignore(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_DIRS or name in IGNORED_FILES or name.startswith(".env.")}


class Workspace:
    def __init__(self, source: Path, test_command: list[str], timeout: int = 60):
        source = source.expanduser().resolve(strict=True)
        if not source.is_dir():
            raise ValueError("Repository path must be a directory")
        if not test_command or any(not isinstance(part, str) or not part for part in test_command):
            raise ValueError("test_command must be a nonempty array of arguments")
        if timeout < 1 or timeout > 300:
            raise ValueError("Test timeout must be between 1 and 300 seconds")
        self._temp = tempfile.TemporaryDirectory(prefix="issue-agent-")
        self.root = Path(self._temp.name) / "repo"
        shutil.copytree(source, self.root, ignore=_ignore, symlinks=True)
        self.test_command = test_command
        self.timeout = timeout
        self.changed_files: set[str] = set()
        self.edit_operations = 0

    def close(self) -> None:
        self._temp.cleanup()

    def __enter__(self) -> "Workspace":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _path(self, relative: str, *, existing: bool = True) -> Path:
        if not relative or Path(relative).is_absolute() or "\\" in relative:
            raise ValueError("Use a repository-relative path with forward slashes")
        pieces = relative.split("/")
        if any(part in {"", ".", ".."} or part.startswith(".env") or part in IGNORED_DIRS for part in pieces):
            raise ValueError("Path is outside the allowed workspace")
        raw_path = self.root / relative
        if any((self.root.joinpath(*pieces[:index])).is_symlink() for index in range(1, len(pieces) + 1)):
            raise ValueError("Symlink paths are not allowed")
        path = raw_path.resolve(strict=False)
        if not path.is_relative_to(self.root):
            raise ValueError("Path is outside the allowed workspace")
        if existing and (not path.is_file() or path.is_symlink()):
            raise ValueError("File does not exist or is not regular")
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            raise ValueError("File type is not editable")
        return path

    def list_files(self) -> dict:
        files = []
        for path in self.root.rglob("*"):
            if path.is_file() and not path.is_symlink() and not any(part in IGNORED_DIRS for part in path.relative_to(self.root).parts):
                files.append(path.relative_to(self.root).as_posix())
        return {"files": sorted(files)[:400], "truncated": len(files) > 400}

    def read_file(self, path: str) -> dict:
        target = self._path(path)
        if target.stat().st_size > MAX_FILE_BYTES:
            raise ValueError("File is too large")
        return {"path": path, "content": target.read_text(encoding="utf-8")}

    def search(self, query: str) -> dict:
        if not query or len(query) > 200:
            raise ValueError("Query must contain 1 to 200 characters")
        matches = []
        for name in self.list_files()["files"]:
            try:
                path = self._path(name)
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if query.lower() in line.lower():
                        matches.append({"path": name, "line": number, "text": line[:300]})
                        if len(matches) == 60:
                            return {"matches": matches, "truncated": True}
            except (UnicodeError, OSError, ValueError):
                continue
        return {"matches": matches, "truncated": False}

    def replace_text(self, path: str, old: str, new: str) -> dict:
        target = self._path(path)
        self._check_editable(path)
        self._check_edit_budget(path)
        if not old or len(new) > MAX_FILE_BYTES:
            raise ValueError("Replacement is empty or too large")
        current = self.read_file(path)["content"]
        count = current.count(old)
        if count != 1:
            raise ValueError(f"Expected one exact match, found {count}")
        updated = current.replace(old, new, 1)
        if len(updated.encode("utf-8")) > MAX_FILE_BYTES:
            raise ValueError("Updated file is too large")
        target.write_text(updated, encoding="utf-8")
        self.changed_files.add(path)
        self.edit_operations += 1
        return {"changed": path}

    def create_file(self, path: str, content: str) -> dict:
        target = self._path(path, existing=False)
        self._check_editable(path)
        self._check_edit_budget(path)
        if target.exists() or len(content.encode("utf-8")) > MAX_FILE_BYTES:
            raise ValueError("File exists or content is too large")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        self.changed_files.add(path)
        self.edit_operations += 1
        return {"created": path}

    def _check_edit_budget(self, path: str) -> None:
        if self.edit_operations >= MAX_EDIT_OPERATIONS:
            raise ValueError("Edit operation limit reached")
        if path not in self.changed_files and len(self.changed_files) >= MAX_CHANGED_FILES:
            raise ValueError("Changed file limit reached")

    @staticmethod
    def _check_editable(path: str) -> None:
        parts = [part.lower() for part in Path(path).parts]
        name = parts[-1]
        if "tests" in parts or name.startswith("test_") or name.endswith("_test.py"):
            raise ValueError("Test files are protected during issue fixing")

    def run_tests(self, command: list[str] | None = None) -> dict:
        selected = list(command or self.test_command)
        if selected[0] == "{python}":
            selected[0] = sys.executable
        try:
            completed = subprocess.run(
                selected,
                cwd=self.root,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=self.timeout,
                env={**{name: value for name, value in os.environ.items() if name.upper() in SAFE_ENV_NAMES}, "PYTHONDONTWRITEBYTECODE": "1"},
                shell=False,
            )
            output = (completed.stdout + "\n" + completed.stderr)[-MAX_OUTPUT_CHARS:]
            return {"exit_code": completed.returncode, "output": output, "timed_out": False}
        except subprocess.TimeoutExpired as exc:
            output = ((exc.stdout or b"") + (exc.stderr or b""))
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            return {"exit_code": None, "output": output[-MAX_OUTPUT_CHARS:], "timed_out": True}
        except OSError as exc:
            return {"exit_code": None, "output": str(exc), "timed_out": False}

    def snapshot_changes(self) -> dict[str, str]:
        """Return only changed text files; original repository remains untouched."""
        result = {}
        for name in sorted(self.changed_files):
            result[name] = self.read_file(name)["content"]
        return result
