import ast
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

LANGUAGE_MAP: Dict[str, str] = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".jsx": "JavaScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".c": "C", ".cpp": "C++",
    ".cc": "C++", ".cs": "C#", ".rb": "Ruby", ".php": "PHP",
    ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".md": "Markdown", ".sql": "SQL", ".r": "R", ".lua": "Lua",
    ".dart": "Dart", ".ex": "Elixir", ".exs": "Elixir",
    ".hs": "Haskell", ".toml": "TOML", ".tf": "Terraform",
}

# Single-line comment prefixes per language
COMMENT_TOKENS: Dict[str, List[str]] = {
    "Python": ["#"], "Ruby": ["#"], "Shell": ["#"], "R": ["#"],
    "JavaScript": ["//"], "TypeScript": ["//"], "Go": ["//"],
    "Rust": ["//"], "Java": ["//"], "C": ["//"], "C++": ["//"],
    "C#": ["//"], "Swift": ["//"], "Kotlin": ["//"], "Scala": ["//"],
    "PHP": ["//", "#"], "Dart": ["//"], "Lua": ["--"], "SQL": ["--"],
    "Haskell": ["--"], "Elixir": ["#"],
}

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".next", "out", "target", "vendor", ".idea",
    ".vscode", ".mypy_cache", ".pytest_cache", "coverage", ".tox",
    "eggs", ".eggs", "site-packages", ".cache", "tmp", "temp",
}

import re

# Only match markers in comment context: "# TODO", "// FIXME:", "<!-- HACK", "* XXX"
TODO_RE = re.compile(r"(?:#|//|/\*|<!--|--|\*)\s*(?:TODO|FIXME|HACK|XXX|BUG)\b", re.IGNORECASE)


@dataclass
class FileMetrics:
    path: str
    language: str
    total_lines: int
    code_lines: int
    blank_lines: int
    comment_lines: int
    size_bytes: int
    todos: List[str] = field(default_factory=list)
    complexity: int = 0


@dataclass
class ScanResult:
    root: str
    files: List[FileMetrics]
    skipped: int


def scan(path: str, exclude: Optional[List[str]] = None) -> ScanResult:
    """Walk a directory tree and collect per-file metrics.

    Skips common build/vendor directories (node_modules, .git, venv, ...)
    plus any extra directory names given in `exclude`. Files with
    unrecognized extensions are counted as skipped, not analyzed.
    """
    exclude_dirs = IGNORE_DIRS | set(exclude or [])
    root = Path(path).resolve()
    files: List[FileMetrics] = []
    skipped = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fname in filenames:
            fpath = Path(dirpath) / fname
            lang = LANGUAGE_MAP.get(fpath.suffix.lower())
            if not lang:
                skipped += 1
                continue
            metrics = _analyze(fpath, lang, root)
            if metrics is None:
                skipped += 1
            else:
                files.append(metrics)

    return ScanResult(root=str(root), files=files, skipped=skipped)


def _analyze(path: Path, language: str, root: Path) -> Optional[FileMetrics]:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        size = path.stat().st_size
    except OSError:
        return None

    lines = content.splitlines()
    blank = sum(1 for ln in lines if not ln.strip())
    prefixes = COMMENT_TOKENS.get(language, [])
    comment = sum(
        1 for ln in lines
        if ln.strip() and any(ln.strip().startswith(p) for p in prefixes)
    )
    code = max(0, len(lines) - blank - comment)

    todos = [ln.strip()[:120] for ln in lines if TODO_RE.search(ln)]

    complexity = _python_complexity(content) if language == "Python" else 0

    return FileMetrics(
        path=str(path),
        language=language,
        total_lines=len(lines),
        code_lines=code,
        blank_lines=blank,
        comment_lines=comment,
        size_bytes=size,
        todos=todos,
        complexity=complexity,
    )


def _python_complexity(source: str) -> int:
    """Approximate cyclomatic complexity for a whole Python file.

    Counts branching nodes (if/for/while/except/with/assert/bool-ops)
    plus one per function definition. Returns 0 if the file fails to parse.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return 0
    score = 0
    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.If, ast.For, ast.While, ast.ExceptHandler,
             ast.With, ast.Assert, ast.comprehension, ast.AsyncFor,
             ast.AsyncWith, ast.Try),
        ):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Each function baseline
            score += 1
    return score
