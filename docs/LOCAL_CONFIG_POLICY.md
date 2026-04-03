# Local Config Policy

This repository separates shared project state from machine-local state.

## Shared and reviewable

- `configs/**`
- `schemas/**`
- `docs/**`
- `src/**`
- `tests/**`
- selected historical summary artifacts under `outputs/**`

## Local-only and untracked

- `.env`
- editor settings and local IDE state
- raw run directories such as `outputs/framework_runs/**`
- local state and lock files such as `outputs/cycle_state.json`
- transfer bundles and handoff files such as `outputs/*.zip` and `outputs/*.pdf`
- new top-level scratch logs and notes such as `outputs/*.log` and `outputs/*.txt`
- machine-specific training exports and temporary demo artifacts

## Important nuance about `outputs/`

The repo already versions selected historical report artifacts for longitudinal
analysis, including cycle history, generated reports, and dashboards. That does
not mean every file under `outputs/` belongs in git.

Rule of thumb:

- Version summary artifacts that support comparison or reporting.
- Do not version raw run payloads, locks, transient state, transfer bundles, or
  one-off local scratch outputs.
- A small set of older top-level log and text files remain tracked as historical
  evidence. Treat them as grandfathered reference artifacts, not canonical
  current outputs to copy forward.

## Practical workflow

- Put secrets and machine-specific paths in `.env`.
- Keep reusable settings in tracked configs or docs.
- If you generate a new output and are not sure whether it belongs in git,
  default to leaving it untracked until the team explicitly decides it is a
  report artifact worth preserving.
