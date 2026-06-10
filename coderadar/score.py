"""Codebase health score: a single 0-100 number with an A-F grade.

Heuristics (each capped, weights sum to 100):
- Documentation (25): comment-to-code ratio, ideal band 5-30%
- Debt (25): TODO/FIXME density per 1k lines of code
- Modularity (25): share of oversized files (>400 lines)
- Complexity (25): mean Python complexity per file (skipped pro-rata
  when the codebase has no Python)
"""

from dataclasses import dataclass
from typing import List

from .metrics import summary
from .scanner import ScanResult

GRADES = [(90, "A", "green"), (75, "B", "bright_green"),
          (60, "C", "yellow"), (40, "D", "orange1"), (0, "F", "red")]


@dataclass
class HealthScore:
    total: int
    grade: str
    color: str
    docs: int
    debt: int
    modularity: int
    complexity: int
    advice: List[str]


def compute(result: ScanResult) -> HealthScore:
    s = summary(result)
    advice: List[str] = []

    # Documentation: 5-30% comment ratio is healthy
    ratio = s["comment_ratio"]
    if ratio >= 5:
        docs = 25 if ratio <= 30 else 18
    else:
        docs = round(ratio / 5 * 25)
    if docs < 15:
        advice.append("Add docstrings/comments - ratio is "
                      f"{ratio}% (healthy: 5-30%)")

    # Debt: todos per 1k code lines (0 -> 25, >=20 -> 0)
    density = s["todos"] / s["code"] * 1000 if s["code"] else 0
    debt = max(0, round(25 - min(density, 20) / 20 * 25))
    if debt < 15:
        advice.append(f"{s['todos']} TODO/FIXME markers - burn down the backlog")

    # Modularity: penalize files over 400 lines
    big = sum(1 for f in result.files if f.total_lines > 400)
    big_share = big / len(result.files) if result.files else 0
    modularity = max(0, round(25 - min(big_share, 0.25) / 0.25 * 25))
    if modularity < 15:
        advice.append(f"{big} file(s) exceed 400 lines - consider splitting")

    # Complexity: mean score across Python files (<=10 ideal, >=50 worst)
    py = [f for f in result.files if f.language == "Python"]
    if py:
        mean_cx = sum(f.complexity for f in py) / len(py)
        complexity = max(0, round(25 - max(0, min(mean_cx, 50) - 10) / 40 * 25))
        if complexity < 15:
            advice.append(f"Mean Python complexity {mean_cx:.0f} - refactor hotspots")
        total = docs + debt + modularity + complexity
    else:
        # No Python: rescale the three applicable components to 100
        complexity = 0
        total = round((docs + debt + modularity) / 75 * 100)

    for cutoff, grade, color in GRADES:
        if total >= cutoff:
            return HealthScore(total, grade, color, docs, debt,
                               modularity, complexity, advice)
    return HealthScore(total, "F", "red", docs, debt, modularity,
                       complexity, advice)
