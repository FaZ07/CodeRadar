from click.testing import CliRunner

from coderadar.cli import main
from coderadar.report import to_markdown
from coderadar.scanner import FileMetrics, ScanResult


def _result():
    f = FileMetrics(
        path="/p/main.py", language="Python", total_lines=100,
        code_lines=80, blank_lines=10, comment_lines=10,
        size_bytes=1024, todos=[], complexity=5,
    )
    return ScanResult(root="/p", files=[f], skipped=0)


def test_markdown_contains_grade_and_tables():
    md = to_markdown(_result())
    assert "CodeRadar Health Report" in md
    assert "Grade **" in md
    assert "| Language |" in md
    assert "`main.py`" in md


def test_cli_md_flag(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")
    runner = CliRunner()
    res = runner.invoke(main, [str(tmp_path), "--md"])
    assert res.exit_code == 0
    assert "CodeRadar Health Report" in res.output


def test_cli_fail_under_passes(tmp_path):
    (tmp_path / "app.py").write_text('"""Doc."""\n# good comment\nx = 1\n')
    runner = CliRunner()
    res = runner.invoke(main, [str(tmp_path), "--json", "--fail-under", "1"])
    assert res.exit_code == 0


def test_cli_fail_under_fails(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")
    runner = CliRunner()
    res = runner.invoke(main, [str(tmp_path), "--json", "--fail-under", "100"])
    assert res.exit_code == 2
