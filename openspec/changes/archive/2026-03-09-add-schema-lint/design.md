## Context

The `database-schema-designer` skill defines schema policies, but enforcement is purely advisory — it relies on the AI agent reading the skill before writing SQL. The `homes` table was created with `created_at` and `updated_at` columns (not in the design doc) and `VARCHAR(n)` columns (should be `TEXT` + `CHECK`), proving the gap. A mechanical linter closes this gap by failing `make check` and CI on policy violations.

## Goals / Non-Goals

**Goals:**
- Enforce all statically-checkable `database-schema-designer` rules via `scripts/lint-schema.sh`
- Integrate into `make check` (and therefore pre-commit hook) and CI `lint.yml`
- Fix all existing violations in `schema.sql` and dependent Go code

**Non-Goals:**
- Runtime / live-DB linting (schemalint-style) — not needed for this project size
- Atlas Pro custom schema rules — unnecessary cost for grep-based checks
- Checking migration files — lint targets `schema.sql` only (the desired-state source of truth)
- EAV pattern detection or JSONB index analysis — require semantic understanding beyond static grep

## Decisions

### Decision 1: Standalone shell script, not embedded in Makefile

**Choice**: `scripts/lint-schema.sh` as a standalone script with a `lint-schema` Makefile target.

**Alternatives considered**:
- Inline in Makefile: Harder to read, test, and extend.
- Go-based linter: Over-engineered for pattern matching on a single SQL file.

**Rationale**: Consistent with `check-migration-drift.sh`. Easy to extend with new rules. Callable from both Makefile and CI independently.

### Decision 2: Six lint rules

**Choice**: Implement these checks as errors (exit 1):

| # | Rule | Pattern | Rationale |
|---|------|---------|-----------|
| 1 | No SERIAL/BIGSERIAL | `\bSERIAL\b`, `\bBIGSERIAL\b` | UUIDv7 is mandatory for PKs |
| 2 | No bare TIMESTAMP | `\bTIMESTAMP\b` (does not match TIMESTAMPTZ) | TIMESTAMPTZ is required |
| 3 | No audit columns | `\b(created_at\|updated_at\|deleted_at)\b` | Prohibited unless design doc requires |
| 4 | No VARCHAR(n) | `VARCHAR\(` | Use TEXT + CHECK constraint |
| 5 | COMMENT ON TABLE coverage | Parse CREATE TABLE names, verify matching COMMENT ON TABLE | Mandatory per skill |
| 6 | COMMENT ON COLUMN coverage | Count columns per table, compare to COMMENT ON COLUMN count | Mandatory per skill |

**Rationale**: These six rules cover all statically-checkable constraints from `database-schema-designer`. Rules 1-4 are simple grep patterns. Rules 5-6 require lightweight parsing (extract table/column names, count matches).

### Decision 3: `make check` integration via separate target

**Choice**: `check: lint lint-schema test` — `lint-schema` as a peer of `lint`, not nested inside it.

**Rationale**: `lint` is Go-specific (gofmt + golangci-lint). Schema linting is a different concern. Separate targets give clear error attribution. The pre-commit hook (`pre-commit-check.sh`) calls `make check`, so no hook changes needed.

### Decision 4: CI `lint.yml` with per-job paths-filter

**Choice**: Add `schema` output to the existing `dorny/paths-filter` step. Add `schema-lint` / `schema-lint-skip` jobs gated on `schema == 'true'`.

**Alternatives considered**:
- New `schema-lint.yml` workflow: Adds workflow count, separate CI Success gate.
- Add to `atlas-ci.yml`: Schema lint is a lint concern, not a migration concern.

**Rationale**: `lint.yml` is the natural home for all lint checks. Per-job filtering avoids running schema lint on Go-only changes. The `schema-lint` job needs only checkout + bash (no Go, no DB), so it's fast.

### Decision 5: Fix existing violations in homes table

**Choice**: In the same change, fix `homes` table violations:
- Remove `created_at` and `updated_at` columns
- Convert `country_code VARCHAR(2)` → `TEXT` + `CHECK (char_length(country_code) = 2)`
- Convert `level_1 VARCHAR(6)` → `TEXT` + `CHECK (char_length(level_1) BETWEEN 2 AND 6)`
- Convert `level_2 VARCHAR(20)` → `TEXT` + `CHECK (level_2 IS NULL OR char_length(level_2) <= 20)`

**Rationale**: The linter must pass on the current schema to be useful. Fixing violations first ensures the linter is green from the start.

### Decision 6: Remove `updated_at` from Go upsert query

**Choice**: Remove `updated_at = now()` from `upsertHomeQuery` in `user_repo.go`. The upsert already updates the data columns via `EXCLUDED.*`, so the row change is tracked implicitly by PostgreSQL's `xmin`/transaction visibility if ever needed.

**Rationale**: The column is being dropped from the table, so the query must be updated. No entity or use case changes needed — `created_at` and `updated_at` were never mapped to Go structs.

## Risks / Trade-offs

- **[grep false positives in comments]** → SQL comments could mention `SERIAL` or `TIMESTAMP` in prose. Mitigation: grep only non-comment lines (strip `--` prefixed lines before checking). Acceptable trade-off for simplicity.
- **[COMMENT ON count mismatch on complex tables]** → Tables with constraints-only lines or multi-line column definitions could cause miscounts. Mitigation: count only lines matching the column definition pattern (indented, type keyword). Test against current schema.
- **[VARCHAR may be intentional in future]** → The skill says "unless strictly required". Mitigation: if a legitimate case arises, add an inline `-- lint:ignore varchar` comment and update the script to respect it. Not implemented now (YAGNI).

## Open Questions

- None. All decisions were resolved during the explore session.
