## Why

`UserUseCase.Get` and `UserUseCase.GetByExternalID`'s specs already state the correct contract — a missing User fails with NotFound, and any other failure to read (e.g. the store being unavailable) is returned with its own code — but both carry `Known defect: liverty-music/backend#471`: the shipped code wraps every repository error with `apperr.Wrap(err, codes.NotFound, ...)`, which replaces the original code, so a database outage was reported to callers as NotFound instead of Unavailable or Internal. Three fan-boundary RPC specs that resolve the caller through `User.GetByExternalID` (Ticket, Concert, Lottery) carry the same defect note because they inherited the masked error code. Once the backend fix (propagate the repository error unchanged, preserving its code) lands, all five specs' existing requirement text is accurate and the stale defect markers should be removed so the specs stop claiming an open defect.

## What Changes

- Remove the `Known defect: liverty-music/backend#471` marker from `components/usecase/user/get` and `components/usecase/user/get-by-external-id` now that the fix makes their existing requirement text (own code preserved on failure) accurate. No requirement wording or scenario changes.
- Remove the same stale marker from the three fan RPC boundary specs that call `User.GetByExternalID` and therefore surfaced the masked code: `components/adapter/fan/api/rpc/ticket`, `components/adapter/fan/api/rpc/concert`, `components/adapter/fan/api/rpc/lottery`. No requirement wording or scenario changes.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/usecase/user/get`: drop the stale known-defect note; requirement text and scenarios are unchanged.
- `components/usecase/user/get-by-external-id`: drop the stale known-defect note; requirement text and scenarios are unchanged.
- `components/adapter/fan/api/rpc/ticket`: drop the stale known-defect note; requirement text and scenarios are unchanged.
- `components/adapter/fan/api/rpc/concert`: drop the stale known-defect note; requirement text and scenarios are unchanged.
- `components/adapter/fan/api/rpc/lottery`: drop the stale known-defect note; requirement text and scenarios are unchanged.

## Impact

- Affected specs: `openspec/specs/components/usecase/user/get/spec.md`, `openspec/specs/components/usecase/user/get-by-external-id/spec.md`, `openspec/specs/components/adapter/fan/api/rpc/ticket/spec.md`, `openspec/specs/components/adapter/fan/api/rpc/concert/spec.md`, `openspec/specs/components/adapter/fan/api/rpc/lottery/spec.md`.
- Affected code (backend repo, tracked by `liverty-music/backend#471`): `internal/usecase/user_uc.go` (`Get` and `GetByExternalID` add context with `fmt.Errorf("...: %w", err)` instead of `apperr.Wrap(err, codes.NotFound, ...)`, preserving the repository's error code).
- No proto or API surface changes.
