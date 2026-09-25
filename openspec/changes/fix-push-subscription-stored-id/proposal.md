## Why

`PushSubscription.Create`'s spec already states the correct contract — the endpoint upsert keeps the row's stored id and reassigns it to the caller — but the note `Known defect: liverty-music/backend#474` flags that the shipped code does not honor it: the repository mints a fresh id whenever the caller omits one, and the use case returns that unstored id instead of the row's real one. Once the backend fix (`RETURNING id` on the upsert) lands, the spec's own text is correct and the stale defect marker should be removed so the spec no longer claims an open defect that is fixed.

## What Changes

- Remove the `Known defect: liverty-music/backend#474` marker from `components/entity/push-subscription/create` and `components/usecase/push-subscription/create` now that the fix makes their existing requirement text (stored id is returned, endpoint reassignment) accurate. No requirement wording or scenario changes — the contract these specs describe was already correct.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/entity/push-subscription/create`: drop the stale known-defect note; requirement text and scenarios are unchanged.
- `components/usecase/push-subscription/create`: drop the stale known-defect note; requirement text and scenarios are unchanged.

## Impact

- Affected specs: `openspec/specs/components/entity/push-subscription/create/spec.md`, `openspec/specs/components/usecase/push-subscription/create/spec.md`.
- Affected code (backend repo, tracked by `liverty-music/backend#474`): `internal/infrastructure/database/rdb/push_subscription_repo.go` (`Create` upsert gains `RETURNING id`), `internal/usecase/push_notification_uc.go` (`Create` sets `sub.ID` from the returned row).
- No proto or API surface changes.
