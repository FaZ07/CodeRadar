from coderadar.scanner import FileMetrics, ScanResult
from coderadar.score import compute


def _file(path="main.py", lang="Python", total=100, code=80, blank=10,
          comment=10, todos=None, complexity=5):
    return FileMetrics(
        path=path, language=lang, total_lines=total, code_lines=code,
        blank_lines=blank, comment_lines=comment, size_bytes=1024,
        todos=todos or [], complexity=complexity,
    )


def test_healthy_codebase_scores_high():
    r = ScanResult(root="/p", files=[_file(), _file("b.py")], skipped=0)
    hs = compute(r)
    assert hs.total >= 90
    assert hs.grade == "A"


def test_debt_heavy_codebase_penalized():
    todos = [f"# TODO {i}" for i in range(50)]
    r = ScanResult(root="/p", files=[_file(todos=todos)], skipped=0)
    hs = compute(r)
    assert hs.debt < 10
    assert any("TODO" in a for a in hs.advice)


def test_no_python_rescales_to_100():
    f = _file("app.js", lang="JavaScript", complexity=0)
    r = ScanResult(root="/p", files=[f], skipped=0)
    hs = compute(r)
    assert 0 <= hs.total <= 100
    assert hs.complexity == 0


def test_huge_files_hurt_modularity():
    files = [_file(f"f{i}.py", total=900, code=800) for i in range(4)]
    r = ScanResult(root="/p", files=files, skipped=0)
    hs = compute(r)
    assert hs.modularity == 0


def test_grade_boundaries():
    r = ScanResult(root="/p", files=[_file()], skipped=0)
    hs = compute(r)
    assert hs.grade in {"A", "B", "C", "D", "F"}
    assert hs.total == hs.docs + hs.debt + hs.modularity + hs.complexity
