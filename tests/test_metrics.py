from coderadar.scanner import FileMetrics, ScanResult
from coderadar import metrics as m


def _make_result(*files):
    return ScanResult(root="/tmp/project", files=list(files), skipped=0)


def _file(path="main.py", lang="Python", total=100, code=70, blank=20, comment=10,
          size=2048, todos=None, complexity=5):
    return FileMetrics(
        path=path, language=lang, total_lines=total, code_lines=code,
        blank_lines=blank, comment_lines=comment, size_bytes=size,
        todos=todos or [], complexity=complexity,
    )


def test_summary_basic():
    r = _make_result(_file(), _file("util.js", "JavaScript", complexity=0))
    s = m.summary(r)
    assert s["files"] == 2
    assert s["lines"] == 200
    assert s["code"] == 140
    assert s["languages"] == 2


def test_summary_empty():
    r = ScanResult(root="/tmp", files=[], skipped=3)
    s = m.summary(r)
    assert s["files"] == 0
    assert s["todos"] == 0
    assert s["comment_ratio"] == 0


def test_language_stats():
    r = _make_result(
        _file("a.py", "Python"),
        _file("b.py", "Python"),
        _file("c.js", "JavaScript"),
    )
    stats = m.language_stats(r)
    assert stats["Python"]["files"] == 2
    assert stats["JavaScript"]["files"] == 1


def test_top_by_lines_order():
    small = _file("small.py", total=10, code=8, blank=1, comment=1)
    big = _file("big.py", total=500, code=400, blank=60, comment=40)
    r = _make_result(small, big)
    top = m.top_by_lines(r, 2)
    assert top[0].path == "big.py"


def test_top_by_complexity():
    low = _file("low.py", complexity=3)
    high = _file("high.py", complexity=99)
    r = _make_result(low, high)
    cx = m.top_by_complexity(r)
    assert cx[0].complexity == 99


def test_all_todos():
    f = _file(todos=["# TODO fix this", "# FIXME urgent"])
    r = _make_result(f)
    todos = m.all_todos(r)
    assert len(todos) == 2
