from pathlib import Path

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import metrics as m
from .scanner import ScanResult
from .score import compute as compute_score

console = Console()

LANG_COLORS = {
    "Python": "blue", "JavaScript": "yellow", "TypeScript": "cyan",
    "Go": "green", "Rust": "red", "Java": "bright_red", "C": "white",
    "C++": "bright_blue", "C#": "magenta", "Ruby": "red3",
    "PHP": "dark_orange", "Swift": "orange1", "Kotlin": "bright_magenta",
    "Scala": "dark_red", "Shell": "bright_green", "HTML": "orange3",
    "CSS": "bright_cyan", "SCSS": "hot_pink", "JSON": "bright_yellow",
    "YAML": "yellow3", "Markdown": "grey82", "SQL": "medium_purple1",
    "R": "steel_blue1", "Lua": "dodger_blue2", "Dart": "sky_blue1",
    "Elixir": "medium_orchid", "Haskell": "violet", "TOML": "pale_green1",
    "Terraform": "medium_purple",
}


def _bar(value: int, total: int, width: int = 20) -> str:
    if total == 0:
        return "-" * width
    filled = round(value / total * width)
    return "#" * filled + "." * (width - filled)


def _fmt_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b //= 1024
    return f"{b:.1f} TB"


def render(result: ScanResult, show_todos: bool = False, show_complexity: bool = False) -> None:
    s = m.summary(result)
    lang_stats = m.language_stats(result)

    console.print()
    console.rule("[bold cyan] CodeRadar [/bold cyan]")
    console.print(f"[dim]  {result.root}[/dim]")
    console.print()

    # ── Health score ──────────────────────────────────────────────────────────
    hs = compute_score(result)
    breakdown = (
        f"[dim]docs {hs.docs}/25   debt {hs.debt}/25   "
        f"modularity {hs.modularity}/25   complexity {hs.complexity}/25[/dim]"
    )
    body = (f"[bold {hs.color}]{hs.grade}[/bold {hs.color}]  "
            f"[bold white]{hs.total}/100[/bold white]\n{breakdown}")
    if hs.advice:
        body += "\n" + "\n".join(f"[yellow]>[/yellow] {a}" for a in hs.advice)
    console.print(Panel(body, title="[bold]Health Score[/bold]",
                        border_style=hs.color, expand=False))
    console.print()

    # ── Summary tiles ──────────────────────────────────────────────────────────
    tiles = [
        Panel(
            f"[bold white]{s['files']}[/bold white]\n[dim]files scanned[/dim]",
            border_style="cyan", expand=True,
        ),
        Panel(
            f"[bold white]{s['lines']:,}[/bold white]\n[dim]total lines[/dim]",
            border_style="cyan", expand=True,
        ),
        Panel(
            f"[bold green]{s['code']:,}[/bold green]\n[dim]code lines[/dim]",
            border_style="green", expand=True,
        ),
        Panel(
            f"[bold yellow]{s['comments']:,}[/bold yellow]\n[dim]comments ({s['comment_ratio']}%)[/dim]",
            border_style="yellow", expand=True,
        ),
        Panel(
            f"[bold red]{s['todos']}[/bold red]\n[dim]tech debt items[/dim]",
            border_style="red", expand=True,
        ),
        Panel(
            f"[bold magenta]{_fmt_size(s['size_bytes'])}[/bold magenta]\n[dim]total size[/dim]",
            border_style="magenta", expand=True,
        ),
    ]
    console.print(Columns(tiles, equal=True))
    console.print()

    # ── Language breakdown ─────────────────────────────────────────────────────
    tbl = Table(
        title="Language Breakdown",
        box=box.ROUNDED,
        border_style="cyan",
        header_style="bold cyan",
        show_lines=False,
    )
    tbl.add_column("Language", min_width=14, style="bold")
    tbl.add_column("Files", justify="right")
    tbl.add_column("Lines", justify="right")
    tbl.add_column("Code", justify="right", style="green")
    tbl.add_column("Comments", justify="right", style="yellow")
    tbl.add_column("Blanks", justify="right", style="dim")
    tbl.add_column("Share", min_width=26)

    total_lines = s["lines"] or 1
    for lang, stat in lang_stats.items():
        color = LANG_COLORS.get(lang, "white")
        pct = stat["lines"] / total_lines * 100
        bar_str = _bar(stat["lines"], total_lines, 20)
        tbl.add_row(
            f"[{color}]{lang}[/{color}]",
            str(stat["files"]),
            f"{stat['lines']:,}",
            f"{stat['code']:,}",
            f"{stat['comments']:,}",
            f"{stat['blanks']:,}",
            f"[{color}]{bar_str}[/{color}] [dim]{pct:.1f}%[/dim]",
        )
    console.print(tbl)
    console.print()

    # ── Largest files ──────────────────────────────────────────────────────────
    top = m.top_by_lines(result, 10)
    if top:
        ftbl = Table(
            title="10 Largest Files",
            box=box.ROUNDED,
            border_style="magenta",
            header_style="bold magenta",
        )
        ftbl.add_column("File", style="dim", no_wrap=False, ratio=3)
        ftbl.add_column("Language", style="bold")
        ftbl.add_column("Lines", justify="right")
        ftbl.add_column("Code", justify="right", style="green")
        ftbl.add_column("Comments", justify="right", style="yellow")
        ftbl.add_column("Size", justify="right", style="magenta")

        for f in top:
            try:
                rel = str(Path(f.path).relative_to(result.root))
            except ValueError:
                rel = f.path
            color = LANG_COLORS.get(f.language, "white")
            ftbl.add_row(
                rel,
                f"[{color}]{f.language}[/{color}]",
                f"{f.total_lines:,}",
                f"{f.code_lines:,}",
                f"{f.comment_lines:,}",
                _fmt_size(f.size_bytes),
            )
        console.print(ftbl)
        console.print()

    # ── Tech debt ─────────────────────────────────────────────────────────────
    if show_todos:
        todos = m.all_todos(result)
        if todos:
            max_show = 25
            tdtbl = Table(
                title=f"Tech Debt - {len(todos)} item(s){' (showing first 25)' if len(todos) > max_show else ''}",
                box=box.ROUNDED,
                border_style="red",
                header_style="bold red",
            )
            tdtbl.add_column("File", style="dim", ratio=2)
            tdtbl.add_column("Note", style="yellow", ratio=4)

            for path, note in todos[:max_show]:
                try:
                    rel = str(Path(path).relative_to(result.root))
                except ValueError:
                    rel = path
                tdtbl.add_row(rel, note)
            console.print(tdtbl)
            console.print()
        else:
            console.print("[green]  No tech debt markers found.[/green]\n")

    # ── Python complexity hotspots ─────────────────────────────────────────────
    if show_complexity:
        cx = m.top_by_complexity(result, 10)
        if cx:
            cxtbl = Table(
                title="Python Complexity Hotspots",
                box=box.ROUNDED,
                border_style="yellow",
                header_style="bold yellow",
            )
            cxtbl.add_column("File", style="dim", ratio=3)
            cxtbl.add_column("Score", justify="right", style="bold")
            cxtbl.add_column("Lines", justify="right")
            cxtbl.add_column("Health")

            for f in cx:
                try:
                    rel = str(Path(f.path).relative_to(result.root))
                except ValueError:
                    rel = f.path
                if f.complexity > 80:
                    color, label = "red", "Critical"
                elif f.complexity > 40:
                    color, label = "yellow", "High"
                elif f.complexity > 15:
                    color, label = "orange1", "Moderate"
                else:
                    color, label = "green", "Low"
                cxtbl.add_row(
                    rel,
                    f"[{color}]{f.complexity}[/{color}]",
                    f"{f.total_lines:,}",
                    f"[{color}]{label}[/{color}]",
                )
            console.print(cxtbl)
            console.print()
        else:
            console.print("[dim]  No Python files found for complexity analysis.[/dim]\n")

    console.rule(f"[dim] {len(result.files)} files | {s['languages']} languages | {_fmt_size(s['size_bytes'])} [/dim]")
    console.print()
