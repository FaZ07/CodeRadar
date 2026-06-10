import json
import sys

import click

from . import __version__
from . import metrics as m
from . import scanner
from .display import console, render


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--exclude", "-e",
    multiple=True,
    metavar="DIR",
    help="Directory name to exclude (repeatable).",
)
@click.option(
    "--todos", "-t",
    is_flag=True,
    help="Show TODO / FIXME / HACK tech-debt items.",
)
@click.option(
    "--complexity", "-c",
    is_flag=True,
    help="Show Python cyclomatic-complexity hotspots.",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output summary as JSON (machine-readable).",
)
@click.option(
    "--md",
    "output_md",
    is_flag=True,
    help="Output report as GitHub-flavored markdown (for PR comments).",
)
@click.option(
    "--fail-under",
    type=click.IntRange(0, 100),
    default=None,
    metavar="N",
    help="Exit with code 2 if health score is below N (CI gate).",
)
@click.option(
    "--top",
    default=10,
    show_default=True,
    metavar="N",
    help="Number of largest files to display.",
)
@click.version_option(__version__, "-v", "--version", prog_name="coderadar")
def main(path: str, exclude: tuple, todos: bool, complexity: bool,
         output_json: bool, output_md: bool, fail_under: int, top: int) -> None:
    # Legacy Windows consoles default to cp1252, which can't print emoji
    """CodeRadar — instant codebase health snapshot.

    Scan PATH (defaults to current directory) and print a rich report showing
    language breakdown, largest files, tech debt, and complexity hotspots.

    \b
    Examples:
      coderadar                        # scan current dir
      coderadar ~/projects/myapp       # scan specific dir
      coderadar . -t -c                # include todos + complexity
      coderadar . -e tests -e docs     # exclude dirs
      coderadar . --json               # machine-readable output
    """
    # Legacy Windows consoles default to cp1252, which can't print emoji
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    result = scanner.scan(path, list(exclude))

    if not result.files:
        console.print("[red]No recognized source files found.[/red]")
        sys.exit(1)

    from .score import compute as compute_score
    hs = compute_score(result)

    if output_json:
        data = m.summary(result)
        data["health"] = {"score": hs.total, "grade": hs.grade, "advice": hs.advice}
        data["language_stats"] = m.language_stats(result)
        click.echo(json.dumps(data, indent=2))
    elif output_md:
        from .report import to_markdown
        click.echo(to_markdown(result))
    else:
        render(result, show_todos=todos, show_complexity=complexity, top=top)

    if fail_under is not None and hs.total < fail_under:
        click.echo(
            f"Health score {hs.total} is below threshold {fail_under}.",
            err=True,
        )
        sys.exit(2)
