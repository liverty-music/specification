## Why

The hype tier "Anywhere" is being renamed to "Away" for consistency and clarity. "Away" better conveys willingness to travel away from home, pairs naturally with the tier progression (Watch → Home → Nearby → Away), and aligns with the existing Japanese label `遠征OK`. This is a terminology rename across proto, backend, frontend, and specs.

## What Changes

- **BREAKING**: Rename proto enum value `HYPE_TYPE_ANYWHERE` to `HYPE_TYPE_AWAY` in `entity/v1/follow.proto`
- Rename Go constant `HypeAnywhere` to `HypeAway` with value `"away"` in `entity/follow.go`
- Update all backend references (mapper, usecase, tests) from `HypeAnywhere`/`"anywhere"` to `HypeAway`/`"away"`
- Add database migration: update existing `'anywhere'` values to `'away'`, change DEFAULT and CHECK constraint
- Update desired-state schema (`schema.sql`) to reflect `'away'`
- Update frontend `HypeType.ANYWHERE` references to `HypeType.AWAY`
- Update i18n keys from `hype.anywhere` to `hype.away` in EN and JA translation files
- Update spec documents to use "Away" terminology

## Capabilities

### New Capabilities

_(None — this is a terminology rename)_

### Modified Capabilities

- `passion-level`: Rename the highest hype tier from "Anywhere" to "Away" in tier definitions and default behavior

## Impact

- **Proto (specification)**: Breaking enum value rename in `entity/v1/follow.proto`; wire value (4) unchanged
- **Backend**: 5 Go files + schema.sql updated; 1 new migration file
- **Frontend**: 1 TypeScript file + 2 i18n JSON files updated
- **Database**: Migration required to rename stored values, DEFAULT, and CHECK constraint
- **Archive files**: Left untouched (historical records)
