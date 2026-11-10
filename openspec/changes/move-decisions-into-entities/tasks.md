Prerequisites: the layering and error sections of `restructure-backend-responsibilities` have merged, and `fix-backend-contract-drift` has fixed the rules marked (B) in design.md. Each section below is one backend PR that passes `make check` on its own; sections 2 to 11 may merge in any order after section 1, and section 12 merges last.

## 1. backend: transition type and the compare-and-set helper

- [ ] 1.1 Add `entity.Transition[S]` (design.md "The entity decides under the repository's lock") with `Changed()`, and an rdb helper that runs `UPDATE … WHERE id = $1 AND <state column> = ANY($from)` and turns 0 affected rows into the lost-race result. Verify with an entity unit test for `Transition` and an rdb test that a stale `From` affects 0 rows
- [ ] 1.2 Convert `LotteryEntryRepository.RevertWin` (`lottery_entry_repo.go:521`) as the reference: `LotteryEntry.RevertWin(reason)` returns the entry and Order transitions, the repository locks, calls it and compare-and-sets. Verify with an entity table test for every entry and Order state and an rdb test for the lost race and the announcement

## 2. backend: Order, payment and refund

- [ ] 2.1 Move Paid and issuance rules to the entity (`Order.MarkPaid`, `NewIssuedTicket`, `Order.IsPaid`, `Order.IssuanceOutcome`, charge eligibility and the captured-counts-as-charged rule) and call them from `order_issue_uc.go`, `order_lottery_workflow.go`, `order_resale_workflow.go` and `issuance_repo.go`. Verify with entity table tests and the existing usecase tests reduced to one per scenario of `usecase/order/*`
- [ ] 2.2 Move refundability, the refund amount, the per-ticket price and the refund plan (`Order.CheckRefundable`, `UnitPrice`, `RefundableAmount`, `RefundPlan`) into the entity; `order_refund_uc.go`, `event_cancelled.go`, `order_refunded.go` and `RefundRepository.CommitRefund` call them, the repository compare-and-sets. Verify with entity table tests for every scenario of `usecase/order/refund` and an rdb lost-race test
- [ ] 2.3 Move settlement status checks, split invariants and the release plan to Settlement. Verify with entity table tests for `entity/settlement` scenarios; `settlement_uc_test.go` keeps orchestration only
- [ ] 2.4 Add `Order.Source()` and use it in `order_confirmation.go`, `adapter/event/analytics_consumer.go` and `adapter/pb/order.go`. Verify with an entity table test for the three sources and a pb test that each source maps to its proto field
- [ ] 2.5 Write the payment purpose explicitly into Stripe metadata at create and read it back without inference (`purchaseFromMetadata`), and move the webhook dispatch by purpose into one usecase method. Verify with a usecase test per purpose and the existing webhook handler test reduced to mapping

## 3. backend: Checkout and ticket stock

- [ ] 3.1 Replace the free count at `checkout_repo.go:203` with `TicketStock.Remaining`, and move the reuse and replacement plan of `GetOrCreateHeld` and the Commit, RevertCommit and RecordCapture outcomes to Checkout (`Checkout.ReplacePlan`, `CanBecome`, outcome methods). Verify with entity table tests and rdb tests for the lost race only
- [ ] 3.2 Move `checkLotteriesDrawn`, `holdingOrderID`, `StartCheckoutWorkflow`'s step choice and `Place`'s status switch to TicketSale and Checkout methods. Verify with entity table tests and `checkout_uc_test.go` / `order_issue_checkout_test.go` reduced to one test per usecase scenario
- [ ] 3.3 Define `Order.CountsTowardLimitAt(now)` and the sold and held predicates, and add parity tests asserting that `orderHeldForEventQuery` (`order_repo.go:80`) and the stock counts (`ticket_stock_repo.go:31-43`) count exactly the rows these predicates accept. Verify the parity tests pass
- [ ] 3.4 Move the seat-type-of-series and no-stock-for-a-cancelled-event checks of `ticket_stock_uc.go:114`, `:121` to `Series.HasSeatType` and `Event.CanBeStocked`. Verify with entity table tests

## 4. backend: Lottery entry

- [ ] 4.1 Remove the restated lottery-sale check from `lottery_entry_repo.go:63-67`, `:206-215` in favour of `ValidateLotteryEntrySale`, and decide "sale open" with `TicketSale.IsOpenAt(entry.CreateTime)` instead of `clock_timestamp()` (`:83`); replace the `time.Now()` reads at `:216`, `:231`, `:410`, `:535` with the entry or caller time. Verify with entity table tests and an rdb test that an entry created at a given time is judged at that time
- [ ] 4.2 Move the lost reasons and the voiding of losers' Orders of `PersistDrawOutcome` and `EndEnteredByEvent` into a LotteryDraw outcome plan applied by compare-and-set, and `StartDrawnEntryWorkflow`'s choice into `LotteryEntry.NextStep`. Verify with entity table tests and rdb lost-race tests
- [ ] 4.3 Define the won and lost predicates behind the entry stats and add a parity test for the stats query (`lottery_entry_repo.go:97-107`). Verify the parity test passes

## 5. backend: Resale entry and listing

- [ ] 5.1 Use one `TicketStock.IsResaleOpenAt` (with the cancelled check) in `resale_entry_ended.go`, `ticket_sale_uc.go`, `resale_listing_uc.go` and `resale_entry_uc.go`. Verify with an entity table test and the usecase tests reduced to orchestration
- [ ] 5.2 Move the create eligibility of `ResaleEntryRepository.Create` (`resale_entry_repo.go:146-211`) into `ResaleEntry.CheckCreate(snapshot)` and the post-draw state of `drawn` (`:537`) into `ResaleEntry.Drawn` transitions; the repository keeps its locks and compare-and-sets. Verify with entity table tests and rdb lost-race tests
- [ ] 5.3 Add a parity test for the free-listing query against `ResaleListing.IsFreeForDrawAt`; replace the two due checks of `resale_draw_workflow.go:52`, `:86` with `entity.ResaleDrawDue` and `shuffleResaleEntries` with `entity.ShuffleDrawOrder`. Verify with entity tests and the parity test
- [ ] 5.4 Move NextDrawTime, the ended-email and sold-refund conditions and ticket ownership to `ResaleEntry.NextDrawTime`, `NeedsEndedEmail`, `ResaleListing.NeedsRefund` and `Ticket.BelongsTo`; `adapter/pb/resale_entry.go` and `adapter/event/resale_entry_consumer.go` stop deciding. Verify with entity table tests

## 6. backend: Ticket and admission

- [ ] 6.1 Move the scan rejection decision of `ticket_uc.go:215-231` into `AdmissionCode.Check(held, eventID)`, and the admission outcome into `Ticket.AdmitOutcome`. Verify with entity table tests for every scenario of the admission usecase spec; `ticket_admit_uc_test.go` keeps orchestration
- [ ] 6.2 Add a parity test asserting that the admit guard of `ticket_repo.go` and the listing check of `resale_listing_repo.go` accept exactly what `Ticket.IsAdmissible` and `IsUsable` accept. Verify the parity test passes
- [ ] 6.3 Move the scanner create and LinkToken visibility conditions and `BindOutcome` to Scanner and Event methods. Verify with entity table tests

## 7. backend: Series, event and concert

- [ ] 7.1 Move the edit policy, slot merge and slot claim of `SeriesRepository.Update`, `takeNewSlot` and `PublishEvents` (`series_events_repo.go:272`, `:365`, `:441`) into Event methods (`CheckChange`, `SlotMergePlan`, `ClaimSlotPlan`), and the cancel policy of `CancelEvents` (`:553`) into `Event.CanTransitionTo` and `Series.CancelPlan`; the repository keeps `lockSeriesForWrite` and `lockSeriesEvents`. Verify with entity table tests for every scenario of `entity/series/update`, `publish-events` and `cancel-events`, and rdb lost-race tests
- [ ] 7.2 Move `eventsToPublish`, Series validation, draft-edit equality and event deletability (`event_removal.go:136`) to Series and Event; add a parity test for the deletability query. Verify with entity table tests and the parity test
- [ ] 7.3 Add parity tests for `fanVisibleCondition`, `catalogEventCondition` and `seriesPublishStateColumn` (`event_conditions.go`) against `Event.IsPubliclyVisible`, the catalog rule and `DerivePublishState`, seeding every combination of discovered or first-party, DRAFT / PUBLISHED / CANCELLED and PUBLIC / UNLISTED. Verify the parity tests pass
- [ ] 7.4 Move dedup, venue normalization, series type and the past-event check out of `gcp/gemini/searcher.go` (`mergeDrafts` `:789`, `seriesTypeOf` `:880`, `:911`) and `gcp/gemini/venue.go:71` into one Event key and matcher, `NormalizeVenueName`, `DiscoveredSeries.ClassifyType` and `DiscoveredEvent.IsBefore`; `concert_creation_uc.go` and `concert_candidate_uc.go` use the same matcher. The searcher returns parsed drafts. Verify with entity table tests; `searcher_test.go` keeps the response mapping
- [ ] 7.5 Move the discovered-concert merge and "new concert to notify" decisions of `ConcertRepository.Create`, the series-type allowlist and the content-addressed first-writer rule into entity methods; the unique indexes stay. Verify with entity table tests and rdb tests for the conflict paths

## 8. backend: Ticket sale and reminders

- [ ] 8.1 Move the create checks of `ticket_sale_uc.go:262-313` into `TicketSale.CheckCreate`, and the discovered-sale identity and result-date merge of `ticket_sale_repo.go:101-109` into `TicketSale.MergeDiscovered`. Verify with entity table tests for `entity/ticket-sale` scenarios
- [ ] 8.2 Move the validity of a found sale out of `gcp/gemini/ticket_sale_searcher.go` (`eventPeriod` `:397`, `:511`) into `DiscoveredTicketSale.Validate(now, ref)`. Verify with entity table tests; the searcher test keeps the response mapping
- [ ] 8.3 Move the reminder audience (`ticket_sale_reminder_uc.go:124`) and delivery outcomes (`ticket_sale_reminder_delivery_uc.go:121`, `:150`) to TicketSale and a reminder outcome type, and decide "a first-party series is never searched" (`ticket_sale_discovery_uc.go:204`) with `Series.IsSearchable`. Verify with entity table tests

## 9. backend: User, identity and organizer

- [ ] 9.1 Choose the current identity verification in Go instead of `ORDER BY status ASC` (`identity_verification_repo.go:39`), move the one-person-per-account and re-verification rules to IdentityVerification, and make the Pocket Sign client return the certificate state for `IdentityVerification.NeedsReverification(state)` to decide (`pocketsign/verify_client.go:417-429`). Verify with entity table tests, including the indeterminate states
- [ ] 9.2 Compute the Home position with `Home.Centroid()` in the usecase and stop calling `infrageo.ResolveCentroid` from `user_repo.go:259`, `:488`. Verify with an entity test and an rdb test that the repository stores the given position
- [ ] 9.3 Replace the hand-rolled resend limiter (`user_uc.go:20-24`) and the other limits with `slidingWindowLimiter` and named constants. Verify with the existing limiter tests and one usecase test per limit
- [ ] 9.4 Move the Provisioning → Active announcement rule and the payout-account deletion blocker of `organizer_repo.go` to Organizer; let the usecase order the provisioning steps of `zitadel/organization_repository.go` and decide the passkey recovery conditions now in `zitadel/passkey_registration_link.go` and `mail/passkey_registration_link.go`. Verify with entity and usecase tests
- [ ] 9.5 Pass the connected-account terms and status mapping of `payment/stripe_settlement.go` from PayoutAccount, and move `emailLanguage` to `User.EmailLanguage`. Verify with entity tests and the client tests reduced to mapping

## 10. backend: Artist, discovery and follow

- [ ] 10.1 Replace the three ended-artist checks (`artist_uc.go:372`, `:396`, `concert_uc.go:412`, ticket sale discovery) with `Artist.IsActive`, and the refresh cadences and failure stops with policy values on the entity. Verify with entity table tests
- [ ] 10.2 Pass the fanart staleness threshold from the entity into `artist_repo.go:58`, `:439` instead of `time.Now()` in the repository, and add its parity test. Verify the parity test passes
- [ ] 10.3 Make the MusicBrainz client return the URL relations and the place clients return candidates; choose with `entity.SelectOfficialSite` and an entity venue matcher in the usecase (`music/musicbrainz/client.go:267`, `maps/google/client.go:152`). Verify with entity table tests; the client tests keep the mapping
- [ ] 10.4 Move the hype rules of `ticket_journey_uc.go:209`, `:226`, `:247` to Follow and TicketJourney, and the search preconditions of `concert_uc.go:583`, `:341` to Artist and a location query type. Verify with entity table tests

## 11. backend: Notifications

- [ ] 11.1 Move the send-once decisions out of `mail/lottery_loss.go`, `mail/resale_sold.go` and `mail/resale_entry_ended.go`: the usecase reads, asks the entity, sends through the mail port and marks. The mail package only sends. Verify with usecase tests using the mockery mocks (the fake stores of the mail tests are removed)
- [ ] 11.2 Move the cancellation-notice, refund-notice, `NotificationTypeSalesReminder` payload, new-concert performer and push device-family rules (`event_cancelled.go:64`, `order_refunded.go:74`, `notification_delivery.go:123`, `notification_new_concerts.go:30`, `adapter/pb/push_notification.go`) to entity methods, and drop the Lost filter of `adapter/event/lottery_entry_drawn_consumer.go:85` in favour of the usecase it calls. Verify with entity table tests
- [ ] 11.3 Replace the seven `x.UserID != caller` checks with `BelongsTo` methods. Verify with entity tests and a grep that no usecase compares a UserID to the caller directly

## 12. backend: function size

- [ ] 12.1 Delete the entity methods that still have no production caller. Verify with a grep per method
- [ ] 12.2 Enable funlen (60 lines, 40 statements), gocognit (20) and cyclop (15) in `.golangci.yml`, excluding `_test.go`. Verify that `make lint` lists the remaining violations
- [ ] 12.3 Split each remaining violation by responsibility. For any function that cannot be split without hurting clarity, ask the user before adding a `//nolint` with its reason. Verify that `make lint` and `make check` pass
