# Changelog

## v1.0.0 — 2026-06-10

First stable release. CLI + GitHub Action.

### Features
- **Health Score (A–F)** — 0–100 grade across documentation, tech debt,
  modularity, and complexity, with actionable advice
- **GitHub Action** — health report as a PR comment + job summary, with
  an optional `fail-under` CI gate
- Language breakdown for 30+ languages (code / comments / blanks)
- Largest-files table (`--top N`)
- Tech-debt radar: `TODO` / `FIXME` / `HACK` / `XXX` / `BUG` in comment
  context only (no false positives from code or strings)
- Python complexity hotspots via AST analysis (`--complexity`)
- Docstring-aware documentation counting for Python
- Output modes: rich terminal dashboard (default), `--json`, `--md`
- `--fail-under N` exits 2 when the score is below N (CI gate)
- Smart ignores: node_modules, .git, venv, dist, __pycache__, etc.
- Runs on Windows, macOS, Linux (UTF-8 safe on legacy consoles)
