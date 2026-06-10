from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from .scanner import FileMetrics, ScanResult


def language_stats(result: ScanResult) -> Dict[str, Dict]:
    stats: Dict[str, Dict] = defaultdict(
        lambda: {"files": 0, "lines": 0, "code": 0, "comments": 0, "blanks": 0}
    )
    for f in result.files:
        s = stats[f.language]
        s["files"] += 1
        s["lines"] += f.total_lines
        s["code"] += f.code_lines
        s["comments"] += f.comment_lines
        s["blanks"] += f.blank_lines
    return dict(sorted(stats.items(), key=lambda x: x[1]["lines"], reverse=True))


def top_by_lines(result: ScanResult, n: int = 10) -> List[FileMetrics]:
    return sorted(result.files, key=lambda f: f.total_lines, reverse=True)[:n]


def top_by_complexity(result: ScanResult, n: int = 10) -> List[FileMetrics]:
    candidates = [f for f in result.files if f.language == "Python" and f.complexity > 0]
    return sorted(candidates, key=lambda f: f.complexity, reverse=True)[:n]


def all_todos(result: ScanResult) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    for f in result.files:
        for note in f.todos:
            items.append((f.path, note))
    return items


def summary(result: ScanResult) -> Dict:
    total_lines = sum(f.total_lines for f in result.files)
    total_code = sum(f.code_lines for f in result.files)
    total_comments = sum(f.comment_lines for f in result.files)
    total_blanks = sum(f.blank_lines for f in result.files)
    total_size = sum(f.size_bytes for f in result.files)
    total_todos = sum(len(f.todos) for f in result.files)

    comment_ratio = round(total_comments / total_code * 100, 1) if total_code else 0

    return {
        "files": len(result.files),
        "skipped": result.skipped,
        "lines": total_lines,
        "code": total_code,
        "comments": total_comments,
        "blanks": total_blanks,
        "comment_ratio": comment_ratio,
        "size_bytes": total_size,
        "todos": total_todos,
        "languages": len(language_stats(result)),
    }
