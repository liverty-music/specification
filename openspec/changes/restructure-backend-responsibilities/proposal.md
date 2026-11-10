## Why

The backend's layers do not hold the responsibilities the project's architecture gives them, and its tests pay for it. This change fixes the structure that the follow-up change `move-decisions-into-entities` builds on: which layer may import which, how an error carries its code, and where the time comes from.

- **Layer imports leak in both directions.**
  - 27 adapter files import infrastructure packages.
  - 18 rdb files import `internal/adapter/pb` to encode announcements.
  - Eight RPC handlers read a repository or an identity-provider port directly instead of going through a usecase.
- **Errors come in two styles.**
  - Most entity validators return plain `errors.New`, and each usecase attaches a code afterwards. Nine call sites do it with `apperr.New(code, err.Error())`, which drops the original error. That is a bug: the cause no longer appears in the logs.
  - Seventeen custom sentinel errors and one custom error type live outside `pkg/`. Callers branch on them with `errors.Is` beside the `apperr` codes, so error handling has two mechanisms.
- **The time comes from several places.** Two entity functions and ten usecase files read the wall clock, while three usecases inject a `Clock`. A test cannot pin the time of the first group.
- **Usecase tests use hand-written fakes** (28 types in 11 files), which backend `AGENTS.md` review criteria forbid.

## What Changes

- **Layer dependencies**
  - Adapters stop importing infrastructure. Each contract the two sides share moves to a place both may import:
    - the event message contract (payload decoding, `ce_subject`, the redelivery mark) and the signed-in caller on the request context move to new `pkg/` packages;
    - the webhook token check and the Series image variant URLs become interfaces the adapter declares;
    - the prefecture names move to `internal/entity`.
  - Infrastructure stops importing adapters. Repositories hand the changed entity to `messaging.Outbox`, which encodes it through an `Encoder` interface that `messaging` declares and `adapter/pb` implements. `internal/di` wires the two.
  - A depguard rule in `.golangci.yml` keeps every dependency pointing inward.
- **Callers through usecases**: every RPC handler resolves its caller and reaches ports through a usecase. This covers the six fan handlers that read `UserRepository` and the identity service's `BackendOrganizationHandler` and `BackendUserHandler`.
- **Errors**
  - Entity validators and guards return `apperr` errors carrying their code, and usecases and repositories pass them through. The codes a client sees do not change.
  - Every `apperr.New(code, err.Error())` keeps the cause.
  - No custom sentinel error or custom error type remains outside `pkg/`. Where a caller must tell two errors of one code apart, the error carries a reason, as proposed in [pannpers/go-apperr#8](https://github.com/pannpers/go-apperr/issues/8). This part waits for that release.
- **Clock**: entities and usecases never read the wall clock. They take the time from their caller or from an injected `Clock`.
- **Tests**: usecase tests stub ports with the mockery mocks instead of hand-written fakes.
- **Workflow docs**: the rule "one PR per repository" is removed from the specification README and AGENTS.md and from backend, frontend and cloud-provisioning `AGENTS.md`. No rule replaces it.

No API, proto, schema or client-visible behaviour changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. The change moves code and error plumbing without changing any outcome or error code a client observes, so `.openspec.yaml` sets `skip_specs: true`.

## Impact

- **Code**: `backend`.
  - `internal/entity`, `internal/usecase`, `internal/adapter/{rpc,event,webhook,pb,linkpreview}`, and `internal/infrastructure/{auth,messaging,geo,gcp/gemini,gcp/storage,database/rdb}`.
  - New packages under `pkg/` (see design.md).
  - `.golangci.yml`, `go.mod` (go-apperr upgrade), and the wiring in `internal/di`.
- **Docs**:
  - backend `AGENTS.md`: "Announcements" and the PR rule.
  - frontend `AGENTS.md`: the PR rule.
  - cloud-provisioning `AGENTS.md`: the PR rule.
  - specification `README.md` and `AGENTS.md`: the PR rule.
- **Dependency**: a go-apperr release that resolves pannpers/go-apperr#8.
- **Follow-up**: `move-decisions-into-entities` moves the business rules onto entities and adds the function-size lint after this change.
- **Not affected**: proto, database schema, cloud-provisioning infrastructure, deployed behaviour.
