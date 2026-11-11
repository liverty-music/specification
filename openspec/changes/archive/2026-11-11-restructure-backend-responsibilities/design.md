## Context

See proposal.md (Why). The measurements below were taken on backend `main` at `0543dba5`.

- **Layer imports.**
  - Adapters use six kinds of thing from infrastructure:
    - `messaging.ParseProtobufData`, `RedeliverLater` and `CloudEventSubject`: 23 uses.
    - `auth.GetClaims`, `GetCallerOrgID` and `Claims`: 13 uses.
    - `auth.WebhookValidator` (a struct): `pre_access_token_handler.go:32`.
    - `auth.OrganizerPublicProcedures`, mentioned in a doc comment of `organizer_handler.go`.
    - `geo.PrefectureName`: `linkpreview/tags.go`.
    - `gcsstorage.VariantObjectKey`: `pb/series.go:37`.
  - 18 rdb files import `internal/adapter/pb` only to build `messaging.Announcement.Payload`, which is a `proto.Message` (`messaging/outbox.go:39`). For example, `issuance_repo.go:237` passes `pb.FromOrder(&paid)`. Three `infrastructure/server` tests also import it, for `pb.NewSeriesImageURLBuilder`; task 1.4 moves that builder and updates them.
  - `entity` and `usecase` import nothing outward.
- **Handlers that skip the usecase layer.**
  - `follow`, `concert`, `push_subscription`, `notification`, `wallet_public_key` and `ticket_journey` call `userRepo.GetByProviderUserID`. `callerUserID` (`lottery_entry_handler.go:44`) calls `UserUseCase.ResolveCaller`, which returns the same User and the same NotFound.
  - `backend_organization_handler.go` and `backend_user_handler.go` call identity-provider ports directly.
- **Entity errors.**
  - Most entity validators return `errors.New`. `user.go:35`, `user.go:70` and `settlement.go:136` say this is the rule.
  - Six entity files already import `go-apperr` (for example `event.go` `CheckChange` and `card_authorization.go`).
  - Callers attach codes after the fact, consistently per rule: InvalidArgument for every validator, and FailedPrecondition for `ValidateLotteryEntrySale`.
  - Some callers use `apperr.Wrap`. Nine use `apperr.New(code, err.Error())`, which drops the cause:
    - `lottery_entry_uc.go:230,237,243`
    - `resale_entry_uc.go:200,206`
    - `ticket_sale_uc.go:272,280,424`
    - `rdb/ticket_sale_search_repo.go:77`
- **Custom errors outside `pkg/`.** go-apperr's `Is` compares the code only (`apperr.go`, `(*AppErr).Is`), so callers that must tell two errors of one code apart use their own sentinels:
  - entity: `ErrScannerNotUsable` (`admission.go:34`), `ErrResaleListingCancelled` (`resale_listing.go:13`), `ErrUnsupportedImage` (`series_image_processor.go:12`), `ErrResaleWinNotRevertible` (`resale_entry.go:159`), `errInvalidAdmissionCode` (`admission_code.go:76`), `errBase45` (`admission_code.go:217`);
  - usecase: `ErrUnknownScannerLinkToken` and `errScannerRefused` (`scanner_uc.go:19,24`), `errSubjectGone` (`notification_subject.go:29`), `ErrPasskeyAccountPending` (`passkey_uc.go:23`);
  - infrastructure: `errInvalidJSON`, `errNoCandidates`, `errTooManyToolCalls`, `errNoText` (`gemini/searcher.go:30-51`), `errNonPublicAddress`, `errOffSiteRedirect`, `errTooManyRedirects` (`gemini/official_pages.go:42-48`), and the type `redeliveryError` (`messaging/redelivery.go:17`).
- **Wall clock.** `identity_verification.go:97` and `ticket_sale_discovery.go:46` call `time.Now()`. `artist_uc`, `settlement_uc` and `lottery_entry_uc` inject a `Clock`, while ten usecase files call `time.Now()`.
- **Hand-written fakes.** 28 fake types in 11 usecase test files, for example `concert_creation_uc_test.go` `fakeConcertRepo`.

## Goals / Non-Goals

**Goals:**
- Every import points inward, and `make lint` enforces it.
- Every error that crosses a package boundary in `internal/` is an `apperr` error. A caller tells errors apart by code, or by code and reason.
- Entities and usecases get the time from their caller or an injected `Clock`.
- Usecase tests stub ports with the mockery mocks.

**Non-Goals:**
- Moving business rules onto entities, the SQL-versus-entity parity tests, and the function-size lint. These are the change `move-decisions-into-entities`, which follows this one: it builds on the layer rules, the error style and the clock set here.
- Changing any outcome or error code a client observes. Doc-comment drift and spec violations are the change `fix-backend-contract-drift`.
- Speeding up the rdb tests and covering untouched packages. That is the change `speed-up-and-fill-backend-tests`.

## Decisions

### Shared contracts move to packages both sides may import

Each contract an adapter and an infrastructure package both use moves to the innermost place both may import, or becomes an interface the adapter declares.

| Contract | New home | Why there |
|---|---|---|
| Event message: decode the protobuf payload, read `ce_subject`, mark a failure "redeliver after d" and read that mark | a new `pkg/` package (for example `pkg/eventmsg`) | Plumbing without business meaning. The redelivery mark is written by the consumer and read by the subscriber, so it must be one definition. It carries a delay, so it stays a custom error type, which `pkg/` may declare. |
| Signed-in caller on the request context (`Claims`, caller Organization id, their context accessors) | a new `pkg/` package (for example `pkg/authctx`) | The interceptors in `infrastructure/auth` write it and handlers read it. The interceptors themselves stay in infrastructure. |
| Webhook token check | an interface declared in `internal/adapter/webhook`, satisfied structurally by `auth.WebhookValidator` | The adapter needs one method, and Go's structural typing needs no import from infrastructure. |
| Prefecture code to name | `internal/entity`, next to `venue_normalize.go` | Domain vocabulary, not an external system. |
| Series image variant URL | The object key stays in `infrastructure/gcp/storage`, where backend#485 put it (the key scheme belongs to the layer that owns object storage). The URL builder moves there too, and `adapter/pb` depends on an interface it declares (`SeriesImageURLs`), wired in `internal/di`. | The storage writer and the CDN URL builder must agree on the key, and only the storage package knows it. |

### Announcements: the Outbox encodes through an interface

`messaging.Announcement.Payload` becomes the changed entity (or the entities of one type one operation changed together), not a `proto.Message`. `messaging` declares:

```go
// Encoder turns an announced entity into its entity/v1 message.
type Encoder interface {
    Encode(subject string, payload any) (proto.Message, error)
}
```

`adapter/pb` implements it (`AnnouncementEncoder`) with a type switch over the announced entity types, choosing the `ForAnnouncement` variant for User and PushSubscription. A ResaleListing is announced as `*entity.ResaleListing`, and the encoder adds its status (both call sites built `usecase.ResaleListingAt{Listing: l, Status: l.Status}`). It satisfies the interface structurally, so it imports nothing from `messaging`. `internal/di` passes it to `messaging.NewOutbox`. Repositories call `announce` with the entity as today, minus the `pb.From…` call.

The call sites are type-checked by a generic helper in `rdb`, which is the one list of what may be announced:

```go
type announced interface {
    *entity.Order | *entity.User | *entity.Checkout | []*entity.Concert // ... every announced type
}

func announce[T announced](ctx context.Context, out Announcer, tx pgx.Tx, subject string, p T) error
```

Passing a type that is not in the list does not compile. Inside `Outbox` and `Encoder` the payload is `any`, because Go allows neither type parameters on methods (so `Outbox.Record` and the `Announcer` interface cannot be generic) nor a union of types outside a constraint. An entity type that is in the list but missing from the encoder's type switch fails the operation with Internal, and an `adapter/pb` table test runs every type of the list through `Encode`.

**Alternatives considered:**
- `Payload []byte`, encoded in the repository. Rejected: the repository would need the entity-to-proto mapping again, which is the dependency this section removes; an injected encoder would still take the entity as its input.
- A marker interface on the entity (`entity.Announced` with an unexported method on each announced type). Rejected: it types the payload all the way into the Outbox, but adds a method to about 17 entity types and spreads the announcement concern across the entity package, while the generic helper keeps the list in one place.
- A new `internal/entitypb` package that both sides import. Rejected: it sits outside the four layers and splits the entity-to-proto mapping across two packages.
- An encoder injected into each repository. Rejected: every announcing repository would take a new dependency, while the Outbox is the one place every announcement passes.

backend `AGENTS.md` ("Announcements") then says that a repository announces the entity and the Outbox encodes it through `adapter/pb`.

### depguard encodes the direction

`.golangci.yml` enables depguard with these rules:

- `internal/entity` imports no `usecase`, `adapter`, `infrastructure` or `di`.
- `internal/usecase` imports no `adapter`, `infrastructure` or `di`.
- `internal/adapter` imports no `infrastructure` or `di`.
- `internal/infrastructure` imports no `adapter` or `di`.
- `pkg` imports no `internal`.

`internal/di` and `cmd/` may import everything.

Test files are exempt (`files: ["…", "!$test"]`). The boundary and story tests wire several layers together on purpose: `adapter/rpc` boundary tests run a handler behind the real `infrastructure/auth` interceptors, `infrastructure/server` tests serve real `adapter/rpc` handlers, and `rdb` story tests record announcements through the real `pb.AnnouncementEncoder`. Production code had no violation left once the rules were enabled.

### Handlers reach ports through usecases

- The six fan handlers take `usecase.UserUseCase` and call the shared `callerUserID`, or `ResolveCaller` where they need the whole User. The NotFound they return is unchanged.
- `BackendOrganizationHandler` and `BackendUserHandler` call a usecase that owns the identity-provider ports they use today. The usecase passes the calls through and returns the same codes.

### Errors: apperr everywhere, a reason where the code is not enough

Entity validators and guards return `apperr.New(codes.InvalidArgument | codes.FailedPrecondition, msg)` with the code each caller attaches today. Callers in `usecase` and `rdb` return them as they are. Where a caller still chooses a code for a foreign error, it uses `apperr.Wrap(err, code, msg)`, so the cause stays in the log. The comments at `user.go:35`, `user.go:70` and `settlement.go:136` are rewritten to state this rule.

No custom sentinel error or custom error type remains in `internal/`. For each one, the deciding question is whether the code it travels with is already unique at the place a caller checks it.

| Today | After | Why |
|---|---|---|
| `ErrScannerNotUsable` | PermissionDenied, code only | `TicketRepository.Admit` returns PermissionDenied only for an unusable scanner (`ticket_repo.go:122`); `ticket_uc.go:185` can check the code. |
| `ErrUnsupportedImage` | InvalidArgument, code only | The image processor returns no other InvalidArgument; its other failures become Internal. |
| `ErrResaleWinNotRevertible` | FailedPrecondition, code only | No production caller branches on it. |
| `errInvalidAdmissionCode`, `errBase45` | InvalidArgument, code only | Used inside `admission_code.go` only. |
| gemini `errNoCandidates`, `errTooManyToolCalls` | Unavailable at creation | `gemini/errors.go` maps them to Unavailable today. |
| gemini `errInvalidJSON`, `errNoText` | Internal at creation | `gemini/errors.go` maps them to Internal today. |
| gemini `errNonPublicAddress`, `errOffSiteRedirect`, `errTooManyRedirects` | FailedPrecondition at creation, code only | No production caller branches on them; only tests read them, through `export_test.go`, and will assert the code instead. |
| `ErrResaleListingCancelled` | FailedPrecondition with reason `RESALE_LISTING_CANCELLED` | `IssuanceRepository.Issue` returns other FailedPreconditions too (`issuance_repo.go:311`), and `order_lottery_workflow.go:305` treats only this one as a result. |
| `ErrUnknownScannerLinkToken`, `errScannerRefused` | PermissionDenied with reason `SCANNER_LINK_TOKEN_UNKNOWN` for the first; no reason for the second | The rate limiter in `di/provider.go:876` counts only unknown tokens. The reason must not reach the client, which must not tell the two refusals apart (`scanner_uc.go:21-23`). |
| `errSubjectGone` | NotFound with reason `NOTIFICATION_SUBJECT_GONE` | Loading a subject reads several records, so NotFound alone does not say the subject is gone. |
| `ErrPasskeyAccountPending` | NotFound with reason `PASSKEY_ACCOUNT_PENDING` | `RecordChange` can return other NotFounds; `passkey_workflow.go:72` waits only on this one. |
| messaging `redeliveryError` | moves to the `pkg/` event message package | It carries a delay, which a code and a reason cannot. `pkg/` may declare it. |

The reason comes from [pannpers/go-apperr#8](https://github.com/pannpers/go-apperr/issues/8). Until its release, the reason rows cannot be done; the code-only rows and every other section of this change do not depend on it and can land first.

One constraint goes back to go-apperr#8: the issue proposes sending the reason to Connect clients in an `ErrorInfo` detail. `SCANNER_LINK_TOKEN_UNKNOWN` must stay on the server. The implementation either uses a go-apperr option to keep a reason off the wire, or, if the release has none, raises it on the issue before relying on the release. go-apperr v1.3.0 settles it: `apperr.WithReason` is logged as `attrs.reason` but never sent to Connect clients, so the scanner refusals reach the client identical; a reception server test compares the two refusals a client receives.

### Time comes from the caller

`NewIdentityVerification` takes the verify time. `DiscoveredTicketSale.Validate` takes `now`. Every usecase reads the injected `Clock` instead of `time.Now()`. Workflows keep reading time inside a step, as backend `AGENTS.md` "Durable workflows" requires.

### Tests use the mockery mocks

The 28 hand-written fake types are replaced with the mockery mocks (`make mocks`), as backend `AGENTS.md` review criteria require. A fake that holds state across calls becomes a mock with ordered expectations.

### The PR rule is removed

The specification `README.md` step 4, the specification `AGENTS.md` workflow step 4 (`CLAUDE.md` is a link to it), backend and frontend `AGENTS.md` line 20, and cloud-provisioning `AGENTS.md` line 16 each say "One PR per repository". No reason is recorded, and no gate depends on it: the archive gate reads the implementing repositories' `main`. The sentence is removed without a replacement, so a change may land in a repository through as many PRs as its review needs. This change's backend work may itself land as several PRs, one per tasks.md section.

## Risks / Trade-offs

- **The error section waits for a library release.** Mitigation: the code-only replacements and every other section land first; the four reason rows are the last task.
- **`Announcement.Payload` loses its static type.** A repository could announce a type the encoder does not handle. Mitigation: the encoder fails with Internal for an unknown type, so the operation stores nothing, and the `adapter/pb` table test lists every announced type.
- **Routing the identity proxy handlers through a usecase adds a pass-through layer.** Accepted: the layer rule then has no exception, and depguard can enforce it.
- **A large diff touching most of `internal/`.** Mitigation: several backend PRs, one per tasks.md section, each passing `make check`.

## Migration Plan

Code and docs only. Nothing to migrate or roll out beyond the normal backend deploy. Rollback is a revert of the PR.
