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
  - 21 infrastructure files import `internal/adapter/pb` to encode announcements (`pb.FromFollow`, `pb.FromCheckout` and others).
  - `entity` and `usecase` import nothing outward.
- **Handlers and the user repository.** `follow`, `concert`, `push_subscription`, `notification`, `wallet_public_key` and `ticket_journey` handlers call `userRepo.GetByProviderUserID`. `callerUserID` (`lottery_entry_handler.go:44`) calls `UserUseCase.ResolveCaller`, which returns the same User and the same NotFound.
- **Entity errors.**
  - Most entity validators return `errors.New`. `user.go:35`, `user.go:70` and `settlement.go:136` say this is the rule.
  - Six entity files already import `go-apperr` (for example `event.go` `CheckChange` and `card_authorization.go`).
  - Callers attach codes after the fact, consistently per rule: InvalidArgument for every validator, and FailedPrecondition for `ValidateLotteryEntrySale`.
  - Some callers use `apperr.Wrap`. Nine use `apperr.New(code, err.Error())`, which drops the cause:
    - `lottery_entry_uc.go:230,237,243`
    - `resale_entry_uc.go:200,206`
    - `ticket_sale_uc.go:272,280,424`
    - `rdb/ticket_sale_search_repo.go:77`
- **Wall clock.** `identity_verification.go:97` and `ticket_sale_discovery.go:46` call `time.Now()`. `artist_uc`, `settlement_uc` and `lottery_entry_uc` inject a `Clock`, while ten usecase files call `time.Now()`.
- **Fan visibility.** `rdb/event_conditions.go` holds `fanVisibleCondition`, `catalogEventCondition` and `seriesPublishStateColumn`. These restate `Event.IsPubliclyVisible` (`event.go:172`), `Concert.IsVisibleToFans` (`concert.go:34`) and `DerivePublishState` (`series.go:155`) in SQL.
- **Function size.** An ad-hoc golangci-lint run reported funlen 29, gocognit 40 and cyclop 15 findings in non-test code. The config was funlen 60/40 with comments ignored, gocognit 20 and cyclop 15. The findings are spread over `cmd/`, `internal/{di,adapter,entity,usecase,infrastructure}` and `pkg/config`.

## Goals / Non-Goals

**Goals:**
- Every rule a usecase spec or entity spec states is computed in one place in Go, on the entity when no store is involved.
- Usecase tests check orchestration only, and entity tests check rules as tables.
- `make lint` enforces the layer direction and function size, so neither regresses.

**Non-Goals:**
- Changing any outcome or error code a client observes. Doc-comment drift and spec violations found during the investigation are the separate change `fix-backend-contract-drift`, which also rewrites the ConcertRepository doc comments on visibility and DRAFT filtering (its task 3.1).
- The identity service's `BackendOrganizationHandler` and `BackendUserHandler`. They call identity-provider ports directly by design: they are thin proxies for the admin console and carry no rule. Routing them through a pass-through usecase would add a layer with nothing in it.
- Speeding up the rdb tests and covering untouched packages. That is the change `speed-up-and-fill-backend-tests`.

## Decisions

### Shared contracts move to packages both sides may import

Each contract an adapter and an infrastructure package both use moves to the innermost place where both may import it. Defining it in the adapter does not work: the infrastructure side would then have to import the adapter.

| Contract | New home | Why there |
|---|---|---|
| Event message: decode the protobuf payload, read `ce_subject`, mark a failure "redeliver after d" and read that mark | a new `pkg/` package (for example `pkg/eventmsg`) | Plumbing without business meaning. The redelivery mark is written by the consumer and read by the subscriber, so it must be one definition. |
| Signed-in caller on the request context (`Claims`, caller Organization id, their context accessors) | a new `pkg/` package (for example `pkg/authctx`) | The interceptors in `infrastructure/auth` write it and handlers read it. The interceptors themselves stay in infrastructure. |
| Webhook token check | an interface declared in `internal/adapter/webhook`, satisfied structurally by `auth.WebhookValidator` | The adapter needs one method, and Go's structural typing needs no import from infrastructure. |
| Prefecture code to name | `internal/entity`, next to `venue_normalize.go` | Domain vocabulary, not an external system. |
| Series image variant URL | The object key stays in `infrastructure/gcp/storage`, where backend#485 put it (the key scheme belongs to the layer that owns object storage). The URL builder moves there too, and `adapter/pb` depends on an interface it declares (`SeriesImageURLs`), wired in `internal/di`. | The storage writer and the CDN URL builder must agree on the key, and only the storage package knows it. |
| Entity to `entity/v1` mapping used by announcements (including the `ForAnnouncement` variants) | a new `internal/entitypb` that imports only `entity` and the generated types | `adapter/pb` and the rdb announcers both import it. |

**Alternative considered:** an announcement-encoder interface injected into each repository. It was rejected because every announcing repository would need a new dependency, and the payload mapping is not a policy that varies per caller.

backend `AGENTS.md` ("Announcements") must then name `internal/entitypb` instead of `internal/adapter/pb`.

### depguard encodes the direction

`.golangci.yml` enables depguard with these rules:

- `internal/entity` imports no `usecase`, `adapter`, `infrastructure` or `di`.
- `internal/usecase` imports no `adapter`, `infrastructure` or `di`.
- `internal/adapter` imports no `infrastructure` or `di`.
- `internal/infrastructure` imports no `adapter` or `di`.
- `internal/entitypb` imports only `entity` and the generated `entity/v1` types.
- `pkg` imports no `internal`.

`internal/di` and `cmd/` may import everything.

### Handlers resolve the caller through UserUseCase

The six handlers take `usecase.UserUseCase` and call the shared `callerUserID`, or `ResolveCaller` where they need the whole User. The NotFound they return is unchanged.

### Rules move to the entity that owns them

For each rule, the entity gains a method or a pure function, and every usecase that restated the rule calls it. A rule that needs a store read keeps the read in the usecase and passes the values in.

| Rule (spec that states it) | Today | On the entity |
|---|---|---|
| 本人確認 gate on a sale, also for "any sale of the event" (`entity/ticket-sale`; the three authorize-card / start usecases) | `lottery_entry_uc.go:314`, `checkout_uc.go:255`, `resale_entry_uc.go:245`, `order_resale_workflow.go:258` | A guard taking the requirement and the fan's IdentityVerification (nil when none). The usecase still reads the verification and turns NotFound into "none". |
| Purchaser full name and phone number required (`entity/user` Personal details; the three usecases) | `lottery_entry_uc.go:239`, `resale_entry_uc.go:202`, `checkout_uc.go:309` | One validator, so `ValidatePersonalDetails` keeps "absent is valid" for stored Users. |
| Only an active Organizer serves (`entity/organizer`) | `organizer_uc.go:478,494,516,533,570,623` | One guard on Organizer. |
| Refund of Tickets still Issued (`usecase/order/refund`) | `order_refund_uc.go:206` `unresoldAmount` | A pure computation over the Order and its Tickets. The usecase reads the Tickets. |
| Settlement split invariants (`entity/settlement`: at least one split, each amount greater than 0) | `settlement_uc.go:234` `buildSplits` | Validation on Settlement. |
| Publish readiness (`usecase/series/publish`) | `series_uc.go:730`, `eventVenueName` at `:755` duplicating `Concert.VenueName` (`concert.go:65`) | A guard on Series over its Events and performers. |
| Deletion blockers (`usecase/user/list-deletion-blockers`) | `user_uc.go:593` | One predicate per record kind. The usecase reads, the entity classifies. |
| Sale window against event start (`entity/ticket-sale`) | `ticket_sale_uc.go:231` `checkEndBeforeEvents`; `checkout_uc.go:206` `openFirstComeSale` | Methods on TicketSale taking the event start times or the instant. |
| Reminder fire time and quiet hours (`usecase/ticket-sale/scan-due-reminders`) | `ticket_sale_reminder_uc.go:265` `scheduledFireTime` | Next to `ReminderStage.Anchor` on the entity, taking the time zone. |
| Ticket sale search interval (`entity/ticket-sale-search`) | `ticket_sale_discovery_uc.go:26` `ticketSaleSearchDue` | On the TicketSaleSearch entity, separate from the reminders: it decides when a Series is searched again, not when a fan is reminded. |
| Same performance (`entity/event`) | `concert_creation_uc.go:561,616`, `concert_candidate_uc.go:283`, entity `FilterNewSeries` (`concert.go:275`) | One venue-date-start key and one matcher on Event, used by all three. |
| Draft-edit equality | `series_uc.go:509` `sameVenue`, `:521` `sameInstant` duplicating `sameOptionalTime` (`event.go:219`) | Event methods. |

The four transition methods with no caller are used where their meaning matches:

- A new `Order.CanBeCharged` (only a Pending Order is charged) replaces `order.Status != OrderStatusPending` at `order_lottery_workflow.go:338` and `order_resale_workflow.go:217`, which decide whether to charge and issue. `Order.CanBecomeVoid` governs the move to Void only and is not used for that check; `Order.CanBePaid` checks the payment details a Paid Order needs, not the status, so neither fits.
- `Event.CanTransitionTo` guards publishing.
- `Checkout.CanBecome` replaces the Held branch at `order_issue_uc.go:129`.
- `ResaleEntry.IsWithdrawable` is used wherever a usecase decides withdrawal.

A method that still has no caller after this is deleted, because dead rules mislead.

Series cancellation of DRAFT Events stays as it is. `components/usecase/series/cancel-events` says a DRAFT Event given to a cancel is removed, not CANCELLED, which matches `Event.CanTransitionTo`.

### Entity errors carry their code

Validators and guards return `apperr.New(codes.InvalidArgument | codes.FailedPrecondition, msg)`, with the code each caller attaches today. Callers in `usecase` and `rdb` return them as they are.

Sentinel errors that callers branch on with `errors.Is` stay sentinels: `ErrScannerNotUsable`, `ErrResaleListingCancelled`, `ErrUnsupportedImage` and `ErrResaleWinNotRevertible`. They are signals between layers, not answers to a client.

The comments at `user.go:35`, `user.go:70` and `settlement.go:136` are rewritten to state this rule.

Where a caller still has to choose a code for a foreign error, it uses `apperr.Wrap(err, code, msg)`, so the cause stays in the log.

**Alternative considered:** named sentinel errors in the entity, mapped by each usecase. It was rejected because every new rule would need a mapping in every caller, and a missing mapping silently becomes Internal.

### Time comes from the caller

`NewIdentityVerification` takes the verify time. `DiscoveredTicketSale.Validate` takes `now`. Usecases that call `time.Now()` read the injected `Clock` instead. Workflows keep reading time inside a step, as backend `AGENTS.md` "Durable workflows" requires.

### Fan visibility: the entity owns the rule, SQL keeps the filter

List queries must filter in SQL to page correctly, so the SQL predicate stays. Two things keep it from drifting:

- The doc comment of every SeriesRepository method that applies `fanVisibilityGuard`, `fanVisibleCondition` or `catalogEventCondition` states that it returns only what fans may see, or that it leaves DRAFT Events out. The ConcertRepository methods are rewritten by `fix-backend-contract-drift` (task 3.1).
- One table test per such method seeds an Event in each combination: discovered or first-party; DRAFT, PUBLISHED or CANCELLED; PUBLIC or UNLISTED. It asserts that the method returns exactly the Events for which `Event.IsPubliclyVisible`, or the catalog rule, holds. `seriesPublishStateColumn` gets the same check against `DerivePublishState`.

### Function size

`.golangci.yml` sets these limits:

- funlen: 60 lines and 40 statements, with comments ignored.
- gocognit: 20.
- cyclop: 15.

`_test.go` files are excluded. `cmd/` is included, the analysis CLIs too.

Each existing violation is fixed by extracting a function per responsibility, not by mechanical slicing. Many usecase violations shrink on their own once the rules move to entities, so splitting happens after the move.

If a function cannot be split without hurting clarity, its `//nolint` is proposed to the user with the reason and added only after they agree. Generated code and `internal/di` constructors are the likeliest candidates.

### Tests

- Each moved rule gets a table test on the entity that covers the scenarios of the spec stating it.
- In usecase tests, cases that only re-checked a moved rule are reduced to one per usecase spec scenario.
- Tests that use hand-written fakes are moved to the mockery mocks, as backend `AGENTS.md` review criteria require. There are 28 fake types in 11 files, for example `concert_creation_uc_test.go` `fakeConcertRepo`.

## Risks / Trade-offs

- **A large diff touching most of `internal/`** is hard to review and conflicts with parallel work. Mitigation: the backend AGENTS.md allows one PR per repository per change, so the work lands as one backend PR whose commits follow the sections of tasks.md (layering, then rules and errors, then lint and splitting). Each commit passes `make check` on its own, so the PR can be reviewed commit by commit.
- **Moving a rule could change an outcome by accident**, for example when two duplicates of a rule differed slightly. Mitigation: before replacing duplicates, diff them. Where they differ, the spec decides, and the difference is reported to the user before merging.
- **The SQL-versus-entity tests need the database.** They run in the rdb suite, which the change `speed-up-and-fill-backend-tests` makes faster.
- **Lint limits could push toward awkward splits.** Mitigation: the "ask before an exclusion" rule above.

## Migration Plan

Code only. Nothing to migrate or roll out beyond the normal backend deploy. Rollback is a revert of the PR.
