import textwrap
from pathlib import Path

import pytest

from coderadar.scanner import _analyze, scan, _python_complexity


def test_python_complexity_basic():
    src = textwrap.dedent("""
        def foo(x):
            if x > 0:
                for i in range(x):
                    pass
            return x
    """)
    score = _python_complexity(src)
    assert score > 0


def test_python_complexity_empty():
    assert _python_complexity("") == 0


def test_python_complexity_syntax_error():
    assert _python_complexity("def (broken:") == 0


def test_analyze_python(tmp_path: Path):
    f = tmp_path / "sample.py"
    f.write_text("x = 1\n# comment\n\nif x:\n    pass  # TODO fix this\n")
    metrics = _analyze(f, "Python", tmp_path)
    assert metrics is not None
    assert metrics.language == "Python"
    assert metrics.total_lines == 5
    assert metrics.blank_lines == 1
    assert metrics.comment_lines == 1
    assert len(metrics.todos) == 1
    assert metrics.complexity > 0


def test_analyze_missing_file(tmp_path: Path):
    result = _analyze(tmp_path / "nonexistent.py", "Python", tmp_path)
    assert result is None


def test_scan_basic(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')\n# TODO do more\n")
    (tmp_path / "util.js").write_text("const x = 1;\n// comment\n")
    (tmp_path / "README.md").write_text("# Project\n")
    (tmp_path / "binary.exe").write_bytes(b"\x00\x01\x02")

    result = scan(str(tmp_path))
    langs = {f.language for f in result.files}
    assert "Python" in langs
    assert "JavaScript" in langs
    assert "Markdown" in langs
    assert result.skipped >= 1  # binary.exe


def test_scan_excludes_node_modules(tmp_path: Path):
    nm = tmp_path / "node_modules"
    nm.mkdir()
    (nm / "lib.js").write_text("module.exports = {};")
    (tmp_path / "app.js").write_text("const x = 1;")

    result = scan(str(tmp_path))
    paths = [f.path for f in result.files]
    assert not any("node_modules" in p for p in paths)
    assert any("app.js" in p for p in paths)


def test_scan_custom_exclude(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("x = 1")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide")

    result = scan(str(tmp_path), exclude=["docs"])
    paths = [f.path for f in result.files]
    assert any("main.py" in p for p in paths)
    assert not any("guide.md" in p for p in paths)
