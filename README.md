# CodeRadar

**Instant codebase health snapshot — in your terminal.**

CodeRadar is a zero-config CLI that scans any project and produces a beautiful, rich dashboard showing language breakdown, largest files, tech-debt markers, and Python complexity hotspots. No API keys, no cloud — just run it.

```
coderadar .
```

```
─────────────────────── CodeRadar ────────────────────────
  /home/user/projects/myapp

┌──────────┐ ┌────────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────┐
│ 84       │ │ 12,431     │ │ 9,102    │ │ 1,204     │ │ 17       │ │ 312.4 KB │
│ files    │ │ total lines│ │ code     │ │ comments  │ │ tech debt│ │ total    │
└──────────┘ └────────────┘ └──────────┘ └───────────┘ └──────────┘ └──────────┘

╭─── Language Breakdown ────────────────────────────────────────────╮
│ Language     Files  Lines   Code   Comments  Blanks  Share        │
│ Python          31   6,841  5,012       712   1,117  ████████ 55% │
│ TypeScript      18   3,201  2,388       291     522  ████  26%    │
│ JavaScript       9   1,204    901        89     214  ██   10%     │
│ YAML             4     103     98          2       3  ░  0.8%     │
│ Markdown         7     612    612          0       0  █  4.9%     │
╰───────────────────────────────────────────────────────────────────╯
```

## Features

- **30+ languages** detected automatically by file extension
- **Line-level breakdown** — code vs. comments vs. blanks per language
- **Largest files** table with per-file stats
- **Tech debt radar** — surfaces every `TODO`, `FIXME`, `HACK`, `XXX`, `BUG` with the file it lives in (`--todos`)
- **Python complexity** — AST-based cyclomatic score per file, colour-coded Critical / High / Moderate / Low (`--complexity`)
- **JSON output** — pipe to `jq`, CI scripts, or dashboards (`--json`)
- Smart ignores — skips `node_modules`, `__pycache__`, `.git`, `venv`, `dist`, etc. automatically

## Installation

```bash
pip install coderadar
```

Or directly from source:

```bash
git clone https://github.com/FaZ07/coderadar
cd coderadar
pip install -e .
```

## Usage

```bash
# Scan current directory
coderadar

# Scan a specific path
coderadar ~/projects/myapp

# Include tech-debt items and complexity hotspots
coderadar . --todos --complexity

# Exclude directories
coderadar . -e tests -e docs -e migrations

# Machine-readable JSON output
coderadar . --json | jq '.language_stats'

# Short flags
coderadar . -t -c
```

### Options

| Flag | Description |
|---|---|
| `PATH` | Directory to scan (default: `.`) |
| `-t`, `--todos` | Show TODO / FIXME / HACK tech-debt items |
| `-c`, `--complexity` | Show Python cyclomatic-complexity hotspots |
| `-e DIR`, `--exclude DIR` | Exclude a directory by name (repeatable) |
| `--json` | Output summary as JSON |
| `--top N` | Number of largest files to display (default: 10) |
| `-v`, `--version` | Show version |
| `-h`, `--help` | Show help |

## Examples

```bash
# Audit a Django project for tech debt
coderadar ~/mydjango -t -e migrations

# Check complexity of a data-science repo
coderadar ~/notebooks -c

# Pipe into a CI badge script
coderadar . --json > report.json
```

## Why CodeRadar?

Most code-analysis tools require configuration files, language servers, or cloud accounts. CodeRadar does one thing well: give you an instant, honest snapshot of what's in a repository — before a PR review, during onboarding, or while evaluating open-source code.

## License

MIT © [Mohamed Fazil](https://github.com/FaZ07)
