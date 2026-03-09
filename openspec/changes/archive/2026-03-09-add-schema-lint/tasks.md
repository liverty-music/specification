## 1. Fix existing schema violations (backend repo)

- [x] 1.1 Edit `schema.sql`: remove `created_at` and `updated_at` columns from `homes` table
- [x] 1.2 Edit `schema.sql`: convert `homes.country_code` from `VARCHAR(2)` to `TEXT` with `CHECK (char_length(country_code) = 2)`
- [x] 1.3 Edit `schema.sql`: convert `homes.level_1` from `VARCHAR(6)` to `TEXT` with `CHECK (char_length(level_1) BETWEEN 2 AND 6)`
- [x] 1.4 Edit `schema.sql`: convert `homes.level_2` from `VARCHAR(20)` to `TEXT` with `CHECK (level_2 IS NULL OR char_length(level_2) <= 20)`
- [x] 1.5 Remove `updated_at = now()` from `upsertHomeQuery` in `user_repo.go`
- [x] 1.6 Generate Atlas migration: `atlas migrate diff --env local fix_homes_table_schema`
- [x] 1.7 Add migration file to `k8s/atlas/base/kustomization.yaml`

## 2. Create schema linter script (backend repo)

- [x] 2.1 Create `scripts/lint-schema.sh` with comment-line stripping (exclude `--` lines)
- [x] 2.2 Implement check: `SERIAL` / `BIGSERIAL` detection (`\bSERIAL\b`, `\bBIGSERIAL\b`)
- [x] 2.3 Implement check: bare `TIMESTAMP` detection (`\bTIMESTAMP\b`)
- [x] 2.4 Implement check: audit column detection (`created_at`, `updated_at`, `deleted_at`)
- [x] 2.5 Implement check: `VARCHAR(` detection
- [x] 2.6 Implement check: COMMENT ON TABLE coverage (every CREATE TABLE has matching COMMENT ON TABLE)
- [x] 2.7 Implement check: COMMENT ON COLUMN coverage (column count matches COMMENT ON COLUMN count per table)
- [x] 2.8 Verify `lint-schema.sh` passes against current `schema.sql`

## 3. Makefile integration (backend repo)

- [x] 3.1 Add `lint-schema` target to `Makefile` that runs `bash scripts/lint-schema.sh`
- [x] 3.2 Update `check` target to `check: lint lint-schema test`
- [x] 3.3 Add `lint-schema` to `.PHONY`

## 4. CI integration (backend repo)

- [x] 4.1 Add `schema` output to `dorny/paths-filter` in `lint.yml` matching `schema.sql` path
- [x] 4.2 Add `schema-lint` job gated on `schema == 'true'` (checkout + `make lint-schema`)
- [x] 4.3 Add `schema-lint-skip` job gated on `schema == 'false'`
- [x] 4.4 Update `ci-success` job to include `schema-lint` and `schema-lint-skip` in `needs` and `allowed-skips`

## 5. Validation (backend repo)

- [x] 5.1 Run `make lint-schema` to verify linter passes
- [x] 5.2 Run `bash scripts/check-migration-drift.sh` to verify migration integrity
