## 1. Proto and plan (specification)

- [ ] 1.1 Add the `ResaleEntry` entity message (order, state Entered/Won/Lost/Lapsed/Withdrawn, create time, draw time, withdraw time, lost reason `ResaleEntryLostReason`: no ticket left, concert cancelled, card could not be charged, payment not completed before the show) and the fan `ResaleEntryService` (AuthorizeCard, Confirm, List, Withdraw) per the rpc-design skill; `ResaleListing` names its resale entry instead of a checkout; `CardAuthorization` gains its expire time; add `resale_entry_id` to the `Order.source` oneof, with `ResaleEntryId` declared in `order.proto` (as `CheckoutId` and `LotteryEntryId` are), because ResaleEntry names its Order and a `resale_entry.proto` declaration would make the two files import each other; verify `make check` (buf lint, format, forbidden words) passes
- [ ] 1.2 Open the plan PR with the `buf skip breaking` label, merge once `CI Success` passes, cut the Release and confirm `buf-release.yml` succeeds (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 2. Schema (backend)

- [ ] 2.1 Add the Atlas migration of design "Migration Plan" (`resale_entries` with `lost_reason` SMALLINT tied to the Lost state by a check, `resale_listings.resale_entry_id` (`checkout_id` is already gone with `remodel-ticket-sales`), `card_authorizations.expire_time`) and update `schema.sql`; verify `atlas migrate validate`, `make lint-schema` and a `migrationtest` that applies and rolls back the migration on an empty resale table

## 3. Card authorization expiry (backend)

- [ ] 3.1 Store the charge's `capture_before` as the card authorization's expire time when it becomes authorized (design D5); check against the Stripe test API with a JPY JCB test card whether the 30-day window applies by default or needs `request_extended_authorization`, and record the answer in design.md D5; verify the scenarios "Before expiry" and "After expiry" of `entity/card-authorization` and a `make test-stripe-e2e` case that reads the expire time

## 4. Entity (components/entity/resale-entry, resale-listing, order)

- [ ] 4.1 Add the ResaleEntry entity with its states, draw times of an event, taking part in a draw, all-or-nothing and the won-but-not-charged rule; verify one unit test per scenario of `entity/resale-entry`
- [ ] 4.2 ResaleListing is free for a draw instead of free to hold, and Order accepts a ResaleEntry source; verify the scenarios of `entity/resale-listing` "Free for a draw" and `entity/order` "An Order has exactly one source"

## 5. Entity operations (backend)

- [ ] 5.1 `ResaleEntry.Create` under the users-row lock of design D2; verify one contract test per scenario of `entity/resale-entry/create`, including "Two applications at once" run concurrently against PostgreSQL
- [ ] 5.2 `ResaleEntry.Get`, `ListByUser`, `ListEnteredByTicketStock` and `SendEndedEmail`; verify one contract test per scenario of each spec
- [ ] 5.3 `ResaleEntry.PersistDrawOutcome` (announcing each recorded entry as `ORDER.resale_entry_changed` in its transaction, `# Announces` in its Go doc) and `ResaleListing.Withdraw` serialized on the stock row (design D4); verify one contract test per scenario of `entity/resale-entry/persist-draw-outcome` and `entity/resale-listing/withdraw`, including "Withdraw and draw at the same moment" run concurrently

## 6. Usecases (backend)

- [ ] 6.1 `ResaleEntryUseCase.AuthorizeCard`, `Confirm` and `List`; verify one unit test per scenario of `usecase/resale-entry/authorize-card`, `confirm` and `list`, and route the card authorization notice of a resale card authorization to `Confirm` (handler test "Fan and notice both confirm")
- [ ] 6.2 `ResaleEntry.Withdraw` locking the stock row of design D8 and announcing the Withdrawn entry as `ORDER.resale_entry_changed` in its transaction, and `ResaleEntryUseCase.Withdraw` returning once the entry is Withdrawn; verify one contract test per scenario of `entity/resale-entry/withdraw` (including an rdb test running Withdraw and `PersistDrawOutcome` for one entry at the same time and finding exactly one of them applied) and one unit test per scenario of `usecase/resale-entry/withdraw`
- [ ] 6.3 `ResaleEntryUseCase.Draw` as the `draw-resale` schedule of design D3 and D4; the scheduled workflow starting `draw-resale:<stock>:<T>` per due stock; verify one unit test per scenario of `usecase/resale-entry/draw` with the operations mocked, that a stock's draw starts no other workflow, and a worker test that a scheduled time draws each stock once and that a failing stock leaves the others drawn
- [ ] 6.3a `Order.Issue` for a Won resale entry's Order (listings Sold, their Tickets Voided, the listing fans' Settlements reduced, in the transaction that makes the Order Paid and announces it); verify one contract test per scenario of `entity/order/issue` "Issue a won resale entry's Order with its listings"
- [ ] 6.4 `ResaleEntry.RevertWin` (entry Lost, Order Void, listings free and the entry announced as `ORDER.resale_entry_changed`, in one transaction), and `OrderUseCase.Issue` issues a Won ResaleEntry, makes it Lost with `RevertWin` when the card can no longer be charged, and at the event's start time releases first and then reverts, or issues when the release finds the card charged; verify one contract test per scenario of `entity/resale-entry/revert-win`, and that `Issue` never calls `RevertWin` while a capture outcome is unknown ("Outcome unknown at the show"), and the scenarios of `usecase/order/issue` "Issue a won resale entry" and "Every Won entry is issued" against the Stripe test API
- [ ] 6.5 The workflow starter, a durable consumer of `ORDER.resale_entry_changed`: start `OrderUseCase.Issue` (`issue:<order>`) for a Won entry and `OrderUseCase.ReleaseCardAuthorization` (`release:<order>`) for a Lapsed, Lost or Withdrawn entry, except a Lost entry whose lost reason is "payment not completed before the show" (Issue already released it), declared as a NACK Consumer manifest in cloud-provisioning `k8s/namespaces/nats/base/jetstream/` and applied before the backend release (the ORDER stream already captures `ORDER.*`, so no stream changes); verify a unit test that a delivery repeated with the same id starts each workflow once
- [ ] 6.5a `Order.Issue` announces each listing it makes Sold (`ORDER.resale_listing_sold`); `ResaleListingUseCase.RefundSold` takes a listing and runs as a workflow with a 24-hour deadline, started as `refund:<listing>` by the workflow starter, a durable consumer of `ORDER.resale_listing_sold` declared as a NACK Consumer manifest in cloud-provisioning `k8s/namespaces/nats/base/jetstream/` and applied before the backend release (the ORDER stream already captures `ORDER.*`, so no stream changes); remove `ResaleListing.ListSoldUnrefunded` and the checkout sweeper goroutine; verify one unit test per scenario of `usecase/resale-listing/refund-sold`, and that a delivery repeated with the same id refunds once
- [ ] 6.6 `NotificationUseCase.SendResaleEntryEnded` in a durable consumer of `ORDER.resale_entry_changed` of its own, declared as a NACK Consumer manifest in cloud-provisioning `k8s/namespaces/nats/base/jetstream/` and applied before the backend release (the ORDER stream already captures `ORDER.*`, so no stream changes), for Lapsed and Lost entries, starting Deliver as `deliver:<type>:<entry>`, with the `resale_entry_lapsed` and `resale_entry_lost` pushes; verify one unit test per scenario of `usecase/notification/send-resale-entry-ended`

## 7. Adapters (backend)

- [ ] 7.1 Upgrade the generated package and add `ResaleEntryHandler`; verify one handler test per scenario of `adapter/fan/api/rpc/resale-entry`

## 8. Stories (backend integration)

- [ ] 8.1 Rewrite the resale story integration test; verify against the Stripe test API every scenario of `stories/resell-a-ticket`: "One of two tickets resold", "Payout after a resale", "Two fans, one listing", "Withdrawn before the draw", "Nobody wins at the last draw", "Authorization about to expire", "Plans changed", "Cancelled before the draw"

## 9. Frontend (fan)

- [ ] 9.1 Upgrade the generated package; add the resale entry screen and the event page's 公式リセール section, and the push texts for `resale_entry_lapsed` and `resale_entry_lost`; verify the component tests of `infrastructure/fan/web/route/resale-entry` and `route/event` "Official resale by lottery in the ticket section", and `make check`
- [ ] 9.2 Run with Playwright on a local build against stubbed RPCs: open a sold-out event, apply for 2 S席, see 申し込みました with the next draw time, reopen the event and see 申し込み済み, then load an entry list with a Lapsed entry and see 期限切れ with the action to apply again; withdraw a waiting entry, confirm, and see 取り消し済み; withdraw against a stub that refuses with FailedPrecondition and see that the draw has already decided the entry

## 10. Legal text

- [ ] 10.1 Update the Terms of Service resale article and add the resale application's 特商法 final confirmation (resale tickets allocated by a daily draw, charged only on a win, the resale deadline); verify one component test per scenario of `global/legal-document` "Terms of Service state the official resale rules" and `route/resale-entry` "特商法 final confirmation of a resale application", and the text on the deployed page

## 11. Release and production check

- [ ] 11.1 Merge the backend PR after `remodel-ticket-sales`, `publish-events-through-outbox`, `make-lottery-draw-durable` and `unify-order-issuance` are released (design Risks), cut the release and confirm in prod (read-only) that the AtlasMigration is applied, the worker logs a `draw-resale` run each minute without errors, and `gh workflow run stripe-sandbox-e2e.yml` succeeds
- [ ] 11.2 Merge the frontend PR, cut the release and confirm the rollout

## 12. Archive

- [ ] 12.1 Remove `CheckoutUseCase.Start`, `CheckoutUseCase.AuthorizeCard` and `OrderUseCase.IssueFromCheckout` from the usecase diagram of `stories/resell-a-ticket` (kept until the story text stops naming them); verify `python3 scripts/check-story-diagrams.py` passes
- [ ] 12.2 Delete the emptied `entity/resale-listing/list-sold-unrefunded` spec; verify `openspec validate --specs` passes
- [ ] 12.3 Add the types `resale_entry_lapsed` and `resale_entry_lost` to the Purpose of `components/entity/notification`; verify `openspec validate --specs` passes
