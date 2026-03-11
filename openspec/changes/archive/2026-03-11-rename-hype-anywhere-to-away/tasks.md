## 1. Specification (Proto + Specs)

- [x] 1.1 Rename `HYPE_TYPE_ANYWHERE` to `HYPE_TYPE_AWAY` in `proto/liverty_music/entity/v1/follow.proto` (keep numeric value 4)
- [x] 1.2 Update comment in `follow.proto` enum header from "ANYWHERE" to "AWAY"
- [x] 1.3 Update `openspec/specs/passion-level/spec.md` tier table: "Anywhere" → "Away", `anywhere` → `away`

## 2. Backend — Entity + Mapper

- [x] 2.1 Rename `HypeAnywhere` to `HypeAway` with value `"away"` in `internal/entity/follow.go`
- [x] 2.2 Update comment on the constant from "HypeAnywhere" to "HypeAway"
- [x] 2.3 Update mapper in `internal/adapter/rpc/mapper/follow.go`: `HypeAnywhere`/`HYPE_TYPE_ANYWHERE` → `HypeAway`/`HYPE_TYPE_AWAY`

## 3. Backend — UseCase + Tests

- [x] 3.1 Update `internal/usecase/push_notification_uc.go`: rename `entity.HypeAnywhere` references and comments
- [x] 3.2 Update `internal/usecase/push_notification_uc_test.go`: rename all `entity.HypeAnywhere` test data
- [x] 3.3 Update `internal/usecase/follow_uc_test.go`: rename all `entity.HypeAnywhere` test data

## 4. Backend — Database Schema + Migration

- [x] 4.1 Update desired-state schema `internal/infrastructure/database/rdb/schema/schema.sql`: DEFAULT `'away'`, CHECK constraint with `'away'`, column comment
- [x] 4.2 Create new migration file: `UPDATE followed_artists SET hype = 'away' WHERE hype = 'anywhere'`, alter DEFAULT, drop/recreate CHECK constraint, update column comment

## 5. Frontend

- [x] 5.1 Update `src/routes/my-artists/my-artists-page.ts`: `HypeType.ANYWHERE` → `HypeType.AWAY`, i18n key `hype.anywhere` → `hype.away`
- [x] 5.2 Update `src/locales/en/translation.json`: rename `anywhere` keys to `away`, update label to "Away"
- [x] 5.3 Update `src/locales/ja/translation.json`: rename `anywhere` keys to `away`
