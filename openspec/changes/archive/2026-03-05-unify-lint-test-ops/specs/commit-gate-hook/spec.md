## ADDED Requirements

### Requirement: Claude Code PreToolUse hook blocks unchecked commits

Each repo SHALL have a Claude Code `PreToolUse` hook configured in `.claude/settings.json` that intercepts `git commit` commands and runs `make check` before allowing the commit to proceed.

#### Scenario: Commit with passing checks

- **WHEN** the AI agent attempts to run `git commit`
- **THEN** the hook MUST run `make check` automatically
- **THEN** if `make check` exits with code 0, the `git commit` MUST be allowed to proceed

#### Scenario: Commit with failing checks

- **WHEN** the AI agent attempts to run `git commit`
- **THEN** the hook MUST run `make check` automatically
- **THEN** if `make check` exits with non-zero code, the `git commit` MUST be blocked

### Requirement: code-verifier skill removal

The `code-verifier` skill at `~/.claude/skills/code-verifier/` SHALL be removed. All references to `code-verifier` in CLAUDE.md and AGENTS.md files SHALL be removed.

#### Scenario: No code-verifier references remain

- **WHEN** the change is complete
- **THEN** no file in any repo SHALL reference `code-verifier`
- **THEN** the `~/.claude/skills/code-verifier/` directory SHALL not exist

### Requirement: CLAUDE.md and AGENTS.md updated

Global CLAUDE.md and per-repo AGENTS.md files SHALL reference Makefile targets (`make lint`, `make test`, `make check`) as the standard development commands.

#### Scenario: AGENTS.md development commands section

- **WHEN** a developer or AI reads the AGENTS.md in any repo
- **THEN** the Development Commands section MUST list `make lint`, `make fix`, `make test`, `make check` as the primary commands
