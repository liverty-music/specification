## Why

The `database-schema-designer` skill defines schema design policies (no audit columns, no SERIAL, no VARCHAR, TIMESTAMPTZ only, COMMENT ON mandatory), but violations are only caught if the AI agent happens to read the skill file. The `homes` table was created with `created_at` and `updated_at` columns that violate the audit column policy, proving the skill-only approach is insufficient. A mechanical linter ensures violations are caught regardless of who or what writes the schema.

## What Changes

- Add `scripts/lint-schema.sh` that statically checks `schema.sql` against design policies:
  - Prohibit `SERIAL` / `BIGSERIAL`
  - Prohibit `TIMESTAMP` (without time zone)
  - Prohibit audit columns (`created_at`, `updated_at`, `deleted_at`)
  - Prohibit `VARCHAR(n)` (use `TEXT` + `CHECK` constraint instead)
  - Detect missing `COMMENT ON TABLE` for each `CREATE TABLE`
  - Detect missing `COMMENT ON COLUMN` (count mismatch per table)
- Add `lint-schema` target to `Makefile`, included in `make check`
- Add `schema.sql` to CI `lint.yml` paths-filter and add `schema-lint` job
- Fix existing violations in `schema.sql` (`homes` table: remove `created_at`/`updated_at`, convert `VARCHAR` to `TEXT` + `CHECK`)

## Capabilities

### New Capabilities
- `schema-lint`: Automated static analysis of schema.sql against database design policies

### Modified Capabilities
- `database-migration`: `make check` now includes `lint-schema` target; CI `lint.yml` gains a `schema-lint` job

## Impact

- `backend/scripts/lint-schema.sh` — new file
- `backend/Makefile` — new `lint-schema` target added to `check`
- `backend/.github/workflows/lint.yml` — paths-filter expanded, new job added
- `backend/internal/infrastructure/database/rdb/schema/schema.sql` — `homes` table modified (drop audit columns, VARCHAR → TEXT + CHECK)
- `backend/k8s/atlas/base/migrations/` — new migration for homes table changes
- `backend/internal/infrastructure/database/rdb/` — Go repository code updated for removed columns and type changes
