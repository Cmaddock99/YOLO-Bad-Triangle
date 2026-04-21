## Summary

- what changed:
- why:

## Quality Checklist

- [ ] The change is the smallest coherent solution for the task.
- [ ] Public behavior is preserved, or the behavior change is intentional and documented.
- [ ] I did not leave dead code, placeholder code, commented-out logic, or untested compatibility hacks.
- [ ] Imports and module boundaries are intentional.
- [ ] Wrappers or shims are explicitly marked and covered by compatibility tests when touched.
- [ ] Docs/comments changed only where they clarify actual behavior.

## Verification

- [ ] `ruff` on the relevant files
- [ ] targeted tests for changed behavior
- [ ] compatibility tests for any wrapper/shim path touched
- [ ] smoke or dry-run verification for CLI/runtime changes when applicable

Commands run:

```text
paste commands here
```

## Risks

- remaining risks or follow-up:
