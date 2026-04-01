# Local Config Governance

This repository separates shared project rules from local machine settings.

- Shared and reviewable: `.cursor/rules/**`, `.env.example`, `configs/**`, docs under `docs/`.
- Local-only (must not be committed): `.env`, `.cursor/settings.json`, editor state, generated outputs under `outputs/` except `outputs/dashboard.html`.

## Policy checks

- CI enforces output hygiene by failing if tracked files under `outputs/` are found outside the allowlist.
- Keep local overrides in ignored files only; promote reusable settings into tracked docs or templates.

## Practical workflow

- Put secrets and machine-specific paths in `.env`.
- Keep team conventions in docs/rules, not editor-local settings.
- If a generated file is accidentally tracked, move it to ignore policy and untrack it in a separate cleanup change.
