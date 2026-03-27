## Why

Backend handler (adapter) and usecase layers contain ~80 manual input validation checks (nil guards, empty string checks, enum lookups) that duplicate what the protovalidate interceptor already enforces via `buf.validate` annotations. This redundancy obscures each layer's true responsibility, inflates code volume, and creates maintenance drift risk when proto schemas evolve. Additionally, the handler layer inconsistently passes either external IDs (`claims.Sub`) or internal UUIDs to usecases, leaking IdP concerns into the domain layer.

## What Changes

- **Remove all manual input validation from handler (adapter) layer** — ~35 checks for nil, empty string, and enum validity that the protovalidate interceptor already rejects before handlers execute.
- **Remove all proto-derived input validation from usecase layer** — ~30 guards on fields that originate from validated proto messages. Usecases will trust all inputs.
- **Remove all `userID == ""` guards from usecase layer** — these checked JWT-derived values; responsibility moves to a single handler helper.
- **Introduce `GetExternalUserID(ctx)` helper** in the mapper package — consolidates claims extraction + empty-sub guard into one function returning `CodeUnauthenticated`.
- **Unify handler identity pattern** — all handlers resolve `claims.Sub` → internal `User.ID` via `GetByExternalID()` before calling usecases. Follow and concert handlers currently pass external IDs directly; they will be aligned.
- **Update follow/concert usecase + repository** to accept internal user UUID instead of external ID.
- **Simplify enum mapping in handlers** — remove `ok` guard from map lookups (interceptor guarantees `defined_only`); convert to direct lookup.

## Capabilities

### New Capabilities

(none — this is a refactoring change with no new user-facing capabilities)

### Modified Capabilities

- `entity-domain-logic`: Usecase layer contract changes — usecases no longer validate inputs, and all user-identifying parameters become internal UUIDs.

## Impact

- **backend/internal/adapter/rpc/**: All handler files modified (validation removal, identity pattern unification).
- **backend/internal/adapter/rpc/mapper/**: New `GetExternalUserID` helper; existing `GetClaimsFromContext` remains for handlers needing full claims.
- **backend/internal/usecase/**: All usecase files modified (validation removal, follow/concert signature changes).
- **backend/internal/infrastructure/database/rdb/**: Follow and concert repository queries updated from external ID to internal UUID.
- **backend/internal/entity/**: `Home.Validate()` retained — cross-field domain invariant not expressible in proto.
- **Tests**: Handler and usecase tests updated to remove validation-specific test cases; follow/concert repository tests updated for internal ID.
- **No proto schema changes** — `buf.validate` annotations already cover all removed checks.
- **No API contract changes** — wire format unchanged; clients unaffected.
