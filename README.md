# CodeRadar

[![CI](https://github.com/FaZ07/CodeRadar/actions/workflows/ci.yml/badge.svg)](https://github.com/FaZ07/CodeRadar/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: zero config](https://img.shields.io/badge/config-zero-brightgreen.svg)](#usage)

**Grade any codebase A–F in one command. No config, no API keys, no cloud.**

CodeRadar scans a project and prints a rich terminal dashboard: an overall **Health Score**, language breakdown, largest files, tech-debt radar, and Python complexity hotspots. Run it before a PR review, during onboarding, or while evaluating an open-source dependency — and know in 2 seconds what you're dealing with.

```
coderadar .
```

```
+----------------------- Health Score ------------------------+
| B  82/100                                                   |
| docs 20/25   debt 17/25   modularity 25/25   complexity 20/25 |
| > 12 TODO/FIXME markers - burn down the backlog             |
+-------------------------------------------------------------+
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

- **Health Score (A–F)** — one number for the whole repo, scored on documentation, tech debt, modularity, and complexity, with actionable advice on what to fix first
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
