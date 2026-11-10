## Context

See proposal.md for why. The facts that shape the approach (backend at `0543dba5`, audit of 2026-11-10):

- Usecases restate rules inline. Examples: `order_issue_uc.go:36` `issueWith` makes an Order Paid and builds Issued Tickets by hand; `order_refund_uc.go:28` `Refund` decides refundability (`:39`, `:48`, `:109`); `organizer_uc.go:478-570` checks the Deactivated status six times; `user_uc.go:20-24` hand-rolls a rate limiter next to `slidingWindowLimiter`.
- Repositories decide in Go and in SQL. Examples:
  - `order_repo.go:80` `orderHeldForEventQuery` is the only definition of "tickets a fan holds for an event", the base of the per-account limit on all three purchase paths.
  - `checkout_repo.go:203` computes the free count again, beside `TicketStock.Remaining`.
  - `series_events_repo.go:272` `Update`, `:365` `takeNewSlot`, `:441` `PublishEvents` and `:553` `CancelEvents` decide the edit, slot-claim and cancel policies.
  - `lottery_entry_repo.go:83` lets the database clock (`clock_timestamp()`) decide whether a TicketSale is open, and `:216`, `:231`, `:410`, `:535` read `time.Now()`.
  - `identity_verification_repo.go:39` decides which verification is current with `ORDER BY status ASC`.
- One repository method already has the target shape: `resale_entry_repo.go:301` `DrawUnderLock` locks the stock, loads a snapshot and runs a decision function passed in from the usecase (`entity.DrawResale`).
- Infrastructure adapters decide: `gcp/gemini/searcher.go:789` `mergeDrafts` dedups and `:880` `seriesTypeOf` classifies; `maps/google/client.go:152` takes the first place; `music/musicbrainz/client.go:267` `selectOfficialSiteURL` chooses the site; `mail/resale_entry_ended.go:61-71` decides whether to send and marks the entity; `pocketsign/verify_client.go:417-429` decides that an indeterminate certificate needs no re-verification.
- Row locks already exist and serialize the writers that matter: `lockTicketStock` (`ticket_stock_repo.go:134`), `lockUserForOrder` (`checkout_repo.go:109`), `lockSeriesForWrite` and `lockSeriesEvents` (`series_events_repo.go:141`, `:153`), `lockSettlement` (`issuance_repo.go:357`), `lockAndCheckEventRemoval` (`event_removal.go:136`).

## Goals / Non-Goals

**Goals:**

- Each rule has one home, named in the tables below, and one Go table test that needs neither mocks nor a database.
- Repositories keep locking, loading, compare-and-set, announcing and mapping, and nothing else.
- Infrastructure adapters return facts from the outside world; entities and usecases decide.
- No function exceeds the lint limits without an exclusion the user agreed to.

**Non-Goals:**

- Changing an outcome, an error code or a stored value a client can observe. Where two copies of a rule disagree today, `fix-backend-contract-drift` decides the correct behaviour from the spec and fixes it first; this change moves the corrected rule.
- The layer direction, the shared contract packages, the apperr convention and the injected `Clock`. These are `restructure-backend-responsibilities`; this change starts after that work merges.
- Making the rdb suite faster. That is `speed-up-and-fill-backend-tests`; this change only shrinks what the suite has to check.

## Decisions

### The entity decides under the repository's lock; the repository compare-and-sets

A write that changes state runs in four steps inside one transaction:

1. The repository takes the same row locks it takes today and loads the rows the decision needs.
2. It calls an entity method, or a decision function the usecase passes in (as `DrawUnderLock` does), with that snapshot.
3. The entity returns a plan: the new values, and for each changed row the states it may change from.
4. The repository applies the plan with `UPDATE … WHERE id = $1 AND state = ANY($from)`, treats 0 affected rows as a lost race (`FailedPrecondition`, or the no-op the spec states for a repeated call), and announces as it does today.

A small generic type in `internal/entity` carries a transition:

```go
// Transition is a state change an entity decided: the state it moves to and
// the states it may move from. A zero Transition changes nothing.
type Transition[S comparable] struct {
	From []S
	To   S
}
```

Example, `LotteryEntryRepository.RevertWin` (`lottery_entry_repo.go:521`): today the repository switches on the entry and Order states and writes both updates. After the change, `LotteryEntry.RevertWin(reason)` returns the entry's and the Order's transitions (and the no-op for an entry already Lost), and the repository only locks, calls it and runs two compare-and-set updates. The transition table is tested in `entity/lottery_entry_test.go`; `lottery_entry_repo_test.go` keeps one test for the lost race and one for the announcement.

**Alternative considered:** move the whole write into the usecase, with the repository offering row-level primitives. Rejected: the usecase would then have to hold a database transaction across calls, and backend `AGENTS.md` ("A write that checks a condition and then acts runs the check and the write in one transaction") is easier to keep when the lock and the write stay in one repository method.

**Alternative considered:** keep the rule in SQL and test it against the database. Rejected: it is the current state, and it is why the same rule exists in SQL and in Go (`fanVisibleCondition` and `Event.IsPubliclyVisible`; `seriesPublishStateColumn` and `DerivePublishState`; `checkout_repo.go:203` and `TicketStock.Remaining`).

### Locks do not change

No write gains or loses a check-then-act. Each method keeps the locks it takes today, so the paths that create the records a check counts still lock the same rows:

- Per-account limit and stock: `lockTicketStock` and `lockUserForOrder`, taken by checkout, lottery entry and resale entry creation, and by issuance.
- Series edits, publish and cancel: `lockSeriesForWrite` and `lockSeriesEvents`.
- Refund and settlement: `lockSettlement`.
- Event removal: `lockAndCheckEventRemoval`.

Moving the decision into Go changes where the condition is evaluated, not which rows are locked when it is evaluated. A method whose check is today a SQL condition evaluated without a lock (`CheckoutRepository.Commit`'s pre-check outside the transaction, `checkout_repo.go:304`) is listed in `fix-backend-contract-drift` together with the missing compare-and-set guards (webhook dedup, `OrganizerRepository.SetStatus`, `UserRepository.UpdateHome`), and is moved here only after that fix.

### What stays in SQL

- **Concurrency guards**: the `WHERE state = ANY($from)` of each compare-and-set, the `hold_expire_at > $now` guard of a holding checkout, unique indexes (one entry per User per TicketSale per Event, `lottery_entry_repo.go` unique key) and partial indexes (`notDraftPredicate`, `event_conditions.go:19`, which is also the predicate of the partial unique index on the natural key). The entity supplies the states and the instant; the SQL only compares.
- **Read filters that paging or batching needs**: `fanVisibleCondition`, `catalogEventCondition`, `seriesPublishStateColumn`, the "due" filters (fanart staleness `artist_repo.go:58`, draws due, searches due), the bounding-box prefilter of `ListByLocation`. Each gets a parity test: the test seeds every combination of the inputs the predicate reads (for visibility: discovered or first-party; DRAFT, PUBLISHED or CANCELLED; PUBLIC or UNLISTED), runs the query, and asserts that it returns exactly the rows the entity predicate accepts. A filter whose threshold is policy (the fanart staleness age, the bounding-box margins) takes the value from the entity as a parameter instead of computing it in the repository.
- **Aggregations a decision reads**: `orderHeldForEventQuery` and the sold and held counts of `ticket_stock_repo.go` stay queries, because they count rows under lock. Their meaning moves to Go: each counted row's contribution is defined by an entity predicate (`Order.CountsTowardLimitAt(now)`, `Checkout.IsHoldingAt`), and a parity test checks the query against it.

### Rules and their homes

The tables group the rules by domain area. "Today" lists the verified locations of each copy; "Home" is the entity method or pure function (an existing name where one exists). Rules marked (B) are fixed first by `fix-backend-contract-drift`.

**Order, payment and refund**

| Rule | Today | Home |
|---|---|---|
| Making an Order Paid and its Tickets Issued | `order_issue_uc.go:36` `issueWith` | `Order.MarkPaid(captured, now)`, `NewIssuedTicket` |
| Whether an Order was already paid | `order_issue_uc.go:81` `isPaid` | `Order.IsPaid` |
| Only a Pending Order of a Won entry is charged | `order_lottery_workflow.go:322` `planIssue`, `order_resale_workflow.go:201` `planResaleIssue` | `Order.CanBeCharged` (added by `restructure-backend-responsibilities`) and `LotteryEntry`/`ResaleEntry` guards |
| An authorization already captured counts as charged when the concert stopped | `order_lottery_workflow.go:252`, `order_resale_workflow.go:86` | `CardAuthorization.CountsAsCharged(eventPublished)` |
| Resale charge cut-off at the event start, and the LostReason for each outcome | `order_resale_workflow.go:70`, `:86-159` | `ResaleEntry.ChargeOutcome(now, start, result)` |
| Refundability by reason and status; Dispute skips the provider refund | `order_refund_uc.go:39`, `:48`, `:109` | `Order.CheckRefundable(reason, event)` |
| Refund of the Tickets still Issued; per-ticket price (B: two formulas today) | `order_refund_uc.go:206` `unresoldAmount`, `event_cancelled.go:172` `pricePerTicket`, `order_refunded.go:97` | `Order.UnitPrice`, `Order.RefundableAmount(tickets)` |
| Consequences of a refund: Issued tickets Voided, Listed listings Cancelled, Sold kept | `refund_repo.go` `CommitRefund` | `Order.RefundPlan(tickets, listings)` applied by compare-and-set |
| Settlement status checks and split invariants | `order_refund_uc.go:73`, `:148`; `settlement_uc.go:234` `buildSplits`; `settlement_uc.go:96` `releaseOne` | `Settlement.IsReversed`, `HasPaidOut`, `ValidateSplits`, `ReleasePlan` |
| Order status to issuance outcome (Paid or Refunded → AlreadyExists, Void → FailedPrecondition) | `issuance_repo.go:141` `Issue` | `Order.IssuanceOutcome` |
| The source of an Order (checkout, lottery entry or resale entry) (B: resale emitted as lottery today) | `order_confirmation.go:102-112`, `analytics_consumer.go:267`, `adapter/pb/order.go:54` | `Order.Source()` |
| Payment purpose from Stripe metadata | `payment/stripe_card_authorization.go:320` `purchaseFromMetadata` | The purpose is written explicitly at create; the reader maps it back without inference |
| Stripe webhook dispatch by purpose and which codes count as acknowledged | `adapter/webhook/stripe_webhook_handler.go:212-214` | One `StripeWebhookUseCase` method |

**Checkout and ticket stock**

| Rule | Today | Home |
|---|---|---|
| Free count of a stock | `checkout_repo.go:203` | `TicketStock.Remaining` (exists) |
| Reuse of a holding checkout; status of a replaced checkout | `checkout_repo.go:163` `GetOrCreateHeld` | `Checkout.ReplacePlan(now)` |
| Commit, RevertCommit and RecordCapture idempotency outcomes | `checkout_repo.go:304`, `:400`, `:456` | `Checkout.CanBecome` (exists) and outcome methods |
| A first-come sale is refused while a closed lottery of the event is undrawn | `checkout_uc.go:218` `checkLotteriesDrawn` | `TicketSale` guard over the event's sales |
| Which checkout of the fan still holds the stock | `checkout_uc.go:237` `holdingOrderID` | `Checkout.IsHoldingAt` (exists) |
| Workflow to start for each checkout status | `checkout_uc.go:349` `StartCheckoutWorkflow` | `Checkout.NextStep` |
| Place: Held, Committed or ended | `order_issue_uc.go:106` `Place` | `Checkout.CanPlace` |
| Tickets a fan holds for an event (per-account limit) | `order_repo.go:80` | `Order.CountsTowardLimitAt(now)` plus parity test |
| Sold and held counts | `ticket_stock_repo.go:31-43` | `Checkout.IsHoldingAt`, `Order.IsSold` plus parity test |
| Seat type of the series; no stock for a cancelled event | `ticket_stock_uc.go:114`, `:121` | `Series.HasSeatType`, `Event.CanBeStocked` |

**Lottery entry**

| Rule | Today | Home |
|---|---|---|
| The TicketSale is a lottery naming the stock's Event | `lottery_entry_repo.go:63-67`, `:206-215`; `entity.ValidateLotteryEntrySale` | `ValidateLotteryEntrySale` (exists), repository stops restating it |
| Sale open at the entry time (database clock today) | `lottery_entry_repo.go:83` | `TicketSale.IsOpenAt(entry.CreateTime)` |
| One entry per TicketSale per Event per fan | `lottery_entry_uc.go:291` `hasEntryForEvent`, unique key | Unique key stays; the usecase check uses a `LotteryEntry` predicate |
| Verification gate | `lottery_entry_uc.go:256` `checkVerification` | Guard from `restructure-backend-responsibilities` |
| RevertWin transition | `lottery_entry_repo.go:521` | `LotteryEntry.RevertWin` returning transitions |
| Lost reason and voiding the losers' Orders after a draw or a cancellation | `lottery_entry_repo.go:377` `PersistDrawOutcome`, `EndEnteredByEvent` | `LotteryDraw` outcome plan |
| Workflow to start for a drawn entry (Won → issue, Lost → release) | `order_lottery_workflow.go:117` `StartDrawnEntryWorkflow` | `LotteryEntry.NextStep` |
| Entry stats (won, lost) | `lottery_entry_repo.go:97-107` | Entity predicates plus parity test |

**Resale entry and listing**

| Rule | Today | Home |
|---|---|---|
| Resale open at a time (three variants today) | `resale_entry_ended.go:22`, `ticket_sale_uc.go`, `resale_listing_uc.go`, `resale_entry_uc.go` | One `TicketStock.IsResaleOpenAt` with the cancelled check |
| Entry eligibility: idempotency on the authorization, open window, one Entered entry per user per event, fits the limit | `resale_entry_repo.go:146-211` | `ResaleEntry.CheckCreate(snapshot)` |
| Free listing for a draw | `resale_entry_repo.go` free-listing query; `ResaleListing.IsFreeForDrawAt` | `IsFreeForDrawAt` (exists) plus parity test |
| Post-draw state of an entry and its Order | `resale_entry_repo.go:537` `drawn` | `ResaleEntry.Drawn` returning transitions |
| Draw due: `ResaleDrawAt` or `ResaleLastDrawMissed`, twice | `resale_draw_workflow.go:52`, `:86` | `entity.ResaleDrawDue` |
| Shuffle of entries | `resale_draw_workflow.go:130` `shuffleResaleEntries` beside `entity.ShuffleDrawOrder` | `entity.ShuffleDrawOrder` |
| NextDrawTime only while Entered | `resale_entry_uc.go:411`, `adapter/pb/resale_entry.go:33` | `ResaleEntry.NextDrawTime` |
| Ended email only for Lapsed or Lost, once | `adapter/event/resale_entry_consumer.go:87`, `mail/resale_entry_ended.go:61-71` | `ResaleEntry.NeedsEndedEmail`; the usecase sends and marks |
| Refund of a sold listing only once | `resale_listing_uc.go:239-243` | `ResaleListing.NeedsRefund` |
| Ticket ownership for a listing | `resale_listing_uc.go:132-139` | `Ticket.BelongsTo` |

**Ticket and admission**

| Rule | Today | Home |
|---|---|---|
| Why a scan is rejected (Forged, OtherEvent) and how many rows it records | `ticket_uc.go:215-231` | `AdmissionCode.Check(held, eventID)` |
| Admissible and usable (three copies) | `ticket_repo.go` admit query; `resale_listing_repo.go`; `Ticket.IsAdmissible`, `IsUsable` | Entity methods plus parity test of the admit guard |
| Failed admission outcome | `ticket_repo.go` admit path | `Ticket.AdmitOutcome` |
| Scanner only for a published event with a start time; LinkToken only while Unused | `scanner_uc.go` create and view | `Scanner` and `Event` guards |
| Scanner bind outcome | `scanner_repo.go` | `Scanner.BindOutcome` |

**Series, event and concert**

| Rule | Today | Home |
|---|---|---|
| Edit policy per state, slot merge | `series_events_repo.go:272` `Update`, `:365` `takeNewSlot`; `series_uc.go:490-521` | `Event.CheckChange` (exists) extended, `Event.SlotMergePlan` |
| Slot claim when publishing | `series_events_repo.go:441` `PublishEvents` | `Event.ClaimSlotPlan(existing *Event)` (the Event already at the slot, if any) |
| Cancel: PUBLISHED → CANCELLED, DRAFT removed, empty Series removed | `series_events_repo.go:553` `CancelEvents`; `series_uc.go:616` | `Event.CanTransitionTo` (exists), `Series.CancelPlan` |
| Which events to publish | `series_uc.go:587` `eventsToPublish` | `Series.EventsToPublish` |
| Publish readiness | `series_uc.go:730`, `:755` | Guard from `restructure-backend-responsibilities` |
| Title and at least one event, in Create and Update | `series_uc.go` Create and Update | `Series.Validate` |
| Deletability of an event | `event_removal.go:136` | `Event.RemovalBlockers` plus parity test |
| Same performance, venue name normalization, dedup inside one search (B: Gemini differs from the entity) | `concert_creation_uc.go:559`, `concert_candidate_uc.go:283`, `gemini/searcher.go:789` `mergeDrafts`, `gemini/venue.go:71`, `entity/concert.go:275`, `entity/venue_normalize.go:57` | One key and matcher on Event; one `NormalizeVenueName` |
| Series type of a discovered series | `gemini/searcher.go:880` `seriesTypeOf` | `DiscoveredSeries.ClassifyType` |
| Past event of a search (B: UTC boundary today) | `gemini/searcher.go:911` | `DiscoveredEvent.IsBefore(day)` |
| Merge of a discovered concert into an existing event | `concert_repo.go` Create natural-key upsert | `Event.MergeDiscovered` plus the unique index |
| New concert to notify about | `concert_repo.go` Create | `ConcertCreation` result |
| Series type allowlist (two copies) | `series_repo.go:298` and the second copy | `SeriesType.IsValid` |
| A first-party series is never searched | `ticket_sale_discovery_uc.go:204` | `Series.IsSearchable` |
| Candidate venue and place-id policy | `concert_candidate_uc.go` | `ConcertCandidate` methods |
| Draft-edit equality | `series_uc.go:509` `sameVenue`, `:521` `sameInstant` | Event methods |

**Ticket sale and reminders**

| Rule | Today | Home |
|---|---|---|
| Window against event starts | `ticket_sale_uc.go:231` `checkEndBeforeEvents`; `checkout_uc.go:203` `openFirstComeSale` | `TicketSale` methods |
| Create: at least one event and an end time, events published and stocked, business details complete | `ticket_sale_uc.go:262-313` | `TicketSale.CheckCreate` |
| Discovered sale identity and result-date merge | `ticket_sale_repo.go:101-109` | `TicketSale.MergeDiscovered` plus unique index |
| Validity of a found sale (start after now, before the last show plus a day, name and end required) | `gemini/ticket_sale_searcher.go:397` `eventPeriod`, `:511` | `DiscoveredTicketSale.Validate(now, ref)` |
| Reminder audience and fire time | `ticket_sale_reminder_uc.go:124`, `:265` | Guard from `restructure-backend-responsibilities` plus `TicketSale.ReminderAudience` |
| NoSubscription counts as sent; no link event skips | `ticket_sale_reminder_delivery_uc.go:121`, `:150` | `ReminderOutcome` |

**User, identity and organizer**

| Rule | Today | Home |
|---|---|---|
| Deletion blockers | `user_uc.go` ListDeletionBlockers | Guard from `restructure-backend-responsibilities` |
| Current identity verification | `identity_verification_repo.go:39` | `IdentityVerification` selection over the user's rows |
| One verified person per account; re-verification marks the old record | `identity_verification_uc.go:212` | `IdentityVerification` methods |
| Re-verification for an indeterminate certificate | `pocketsign/verify_client.go:417-429` | `IdentityVerification.NeedsReverification(state)`; the client returns the state |
| Home position | `infrastructure/geo/resolver.go:20`, `user_repo.go:259`, `:488` | `Home.Centroid()`; the repository stores what the usecase computed |
| Rate limits (resend 3 per 10 min, recovery, verify email, sign-in links) | `user_uc.go:20-24`, `organizer_uc.go` | `slidingWindowLimiter` (exists) for all, limits as named constants |
| Organizer that may act; Delete requires Deactivated | `organizer_uc.go:478-570` | Guard from `restructure-backend-responsibilities` |
| Announce only on Provisioning → Active; payout account blocks deletion | `organizer_repo.go` | `Organizer` transition and `RemovalBlockers` |
| Organization provisioning steps and owner exceptions | `zitadel/organization_repository.go` Provision, `:558` `ownerUserName` | Usecase orders the steps; the IdP client performs one step per call |
| Passkey recovery: issued only for a verified IdP email, sent to which address | `zitadel/passkey_registration_link.go:90-98`, `mail/passkey_registration_link.go` | Usecase decides; the IdP client reports verification and issues the code |
| Payout account status mapping and connected-account terms | `payment/stripe_settlement.go:26-29`, `mapAccountStatus` | `PayoutAccount` terms passed to the provider |
| Email language | `mail/passkey_registration_link.go` `emailLanguage` | `User.EmailLanguage` |

**Artist, discovery and follow**

| Rule | Today | Home |
|---|---|---|
| An ended artist is not suggested or searched (three copies) | `artist_uc.go:372`, `:396`; `concert_uc.go:412`; ticket sale discovery | `Artist.IsActive` |
| Refresh cadence and stop after consecutive failures | `artist_uc.go`, `official_site_refresh_uc.go:19`, `:63`, `:205` | `RefreshPolicy` values on the entity |
| Fanart staleness | `artist_repo.go:58`, `:439` | Threshold from the entity, parity test |
| Official site selection among MusicBrainz relations | `music/musicbrainz/client.go:267` | `entity.SelectOfficialSite(name, candidates)` |
| Venue place among search results | `maps/google/client.go:152` `Places[0]` | Client returns candidates; the usecase picks with an entity matcher |
| Same MBID is the same artist; first name wins | `artist_repo.go` Create | `Artist` merge rule plus the unique index |
| Hype raised only for one followed performer and certain journey states | `ticket_journey_uc.go:209`, `:226`, `:247` | `Follow` and `TicketJourney` methods |
| An artist needs a name and an MBID to be searched; location range at most 30 days | `concert_uc.go:583`, `:341` | `Artist.IsSearchable`, `LocationQuery.Validate` |

**Notifications**

| Rule | Today | Home |
|---|---|---|
| Loss, sold and ended emails sent once, marked after sending | `mail/lottery_loss.go:59-66`, `mail/resale_sold.go:59-66`, `mail/resale_entry_ended.go:61-71` | Usecase reads, asks the entity (`NeedsLossEmail` and friends), sends through the mail port and marks |
| Lost filter of the drawn-entry consumer | `adapter/event/lottery_entry_drawn_consumer.go:85` | The usecase it calls |
| Cancellation notice only for Paid Orders | `event_cancelled.go:64`, `:122` | `Order.NeedsCancellationNotice` |
| Refund notice only for a Cancellation refund above 0 | `order_refunded.go:74` | `Refund.NeedsNotice` |
| TicketSaleReminder payload (`NotificationTypeSalesReminder`) | `notification_delivery.go:123` | `Notification.Message` |
| New-concert notification performer filter | `notification_new_concerts.go:30` | `Concert.HasPerformer` |
| Device family of a push endpoint | `adapter/pb/push_notification.go:13-19` | `PushSubscription.DeviceFamily` |

Ownership checks (`x.UserID != caller`, seven usecases) become one `BelongsTo` method per entity.

### Function size

`.golangci.yml` enables funlen (60 lines, 40 statements, comments ignored), gocognit (20) and cyclop (15). `_test.go` files are excluded; `cmd/` and the analysis CLIs are included. The section that adds them comes last, because the moves above rewrite most of the functions behind the 84 findings these values report today (29 funlen, 40 gocognit, 15 cyclop; measured 2026-11-10). Each remaining violation is split by responsibility. A `//nolint` is proposed to the user with its reason and added only after they agree.

### Tests

- Each moved rule gets an entity table test covering the scenarios of the spec that states it.
- Usecase tests keep one test per usecase spec scenario, with the operations mocked, and drop the cases that re-checked a moved rule.
- Repository tests keep, per compare-and-set, the lost-race case and the announcement; per SQL filter or aggregation, the parity test.
- Infrastructure client tests keep the mapping from the external response to the returned facts.

## Risks / Trade-offs

- [Two copies of a rule that disagree] → The disagreement is a bug for `fix-backend-contract-drift`, which fixes it from the spec before this change moves it. When a section here finds a new disagreement, it stops and reports it to the user instead of choosing.
- [A decision moved out of SQL is evaluated against a snapshot that a concurrent writer changes] → The snapshot is read under the locks listed above, and the compare-and-set rejects a change from an unexpected state, so a lost race fails or is a no-op, never a silent overwrite.
- [The diff is large] → Each tasks.md section is one PR that passes `make check` on its own and leaves the tree consistent; sections can merge in any order after section 1.
- [Lint limits push toward awkward splits] → The ask-before-exclusion rule above.

## Migration Plan

Code only. Each section merges and deploys as a normal backend release; a section is rolled back by reverting its PR.
