## Why

CI failures caused by lint/format/test issues that should have been caught locally before commit (issues #133-136). The root cause is that each repo has different check commands scattered across AGENTS.md and the code-verifier skill, with no unified interface. The AI agent sometimes skips or runs wrong commands, and there is no structural enforcement.

## What Changes

- Add a `Makefile` to each repo (backend, frontend, specification, cloud-provisioning) with unified targets: `lint`, `fix`, `test`, `test-integration`, `check`
- Introduce a Claude Code `PreToolUse` hook that automatically runs `make check` before any `git commit`, structurally preventing unchecked commits
- Modify CI workflows to call `make lint` / `make test-integration` instead of inline commands, ensuring CI and local checks use the same logic
- Remove the `code-verifier` skill (replaced by the hook)
- Fix the existing CI failures (issues #133, #134, #135, #136)

## Capabilities

### New Capabilities

- `unified-check-interface`: Makefile-based lint/fix/test/check targets providing a single entry point across all repos
- `commit-gate-hook`: Claude Code PreToolUse hook that blocks `git commit` unless `make check` passes

### Modified Capabilities

None — this change is infrastructure/tooling only and does not modify any spec-level behavior.

## Impact

- **All repos** (backend, frontend, specification, cloud-provisioning): New `Makefile` added, CI workflows updated
- **Claude Code config**: New hook in each repo's `.claude/settings.json`; `code-verifier` skill removed from `~/.claude/skills/`
- **AGENTS.md / CLAUDE.md**: Updated to reference Makefile targets instead of individual commands
- **CI**: Workflow files updated to use `make` targets; no functional change in what is checked, only how it is invoked
