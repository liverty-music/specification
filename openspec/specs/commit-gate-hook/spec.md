# Capability: commit-gate-hook

## Purpose

Ensures that AI agents (Claude Code) cannot commit code without first passing automated quality checks. Each repo has a Claude Code `PreToolUse` hook that intercepts `git commit` and runs `make check` as a gate.

## Requirements

### Requirement: code-verifier skill removal

The `code-verifier` skill at `~/.claude/skills/code-verifier/` SHALL be removed. All references to `code-verifier` in CLAUDE.md and AGENTS.md files SHALL be removed.

#### Scenario: No code-verifier references remain

- **WHEN** the change is complete
- **THEN** no file in any repo SHALL reference `code-verifier`
- **THEN** the `~/.claude/skills/code-verifier/` directory SHALL not exist
