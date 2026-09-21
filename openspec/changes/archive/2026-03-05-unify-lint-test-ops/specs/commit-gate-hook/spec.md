## ADDED Requirements

### Requirement: code-verifier skill removal

The `code-verifier` skill at `~/.claude/skills/code-verifier/` SHALL be removed. All references to `code-verifier` in CLAUDE.md and AGENTS.md files SHALL be removed.

#### Scenario: No code-verifier references remain

- **WHEN** the change is complete
- **THEN** no file in any repo SHALL reference `code-verifier`
- **THEN** the `~/.claude/skills/code-verifier/` directory SHALL not exist
