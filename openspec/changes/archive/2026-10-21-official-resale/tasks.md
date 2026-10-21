## 1. Specification — main-spec Purposes and the plan PR

- [x] 1.1 Edit the main spec Purposes directly (proposal "(Purpose)"), and verify `openspec validate --specs` and `python3 scripts/check-spec-layout.py` pass:
  - `components/entity/ticket-type`: add the rows `resale open time` (when its sold count first equalled its quantity; absent until then; set once) and `free resale count` (its ResaleListings free when read; FirstCome only; derived when read), and `TicketType ||--o{ ResaleListing : "is resold through"` to the erDiagram;
  - `components/entity/checkout`: add "or, for a resale Checkout, the ResaleListings it holds" to the Purpose sentence and `Checkout |o--o{ ResaleListing : "holds"` to the erDiagram;
  - `components/entity/order`: add `Order ||--o{ ResaleListing : "is refunded through"` to the erDiagram;
  - `components/entity/ticket`: add `Ticket ||--o{ ResaleListing : "is offered by"` to the erDiagram.
- [x] 1.3 Open the plan PR from a worktree cut from origin/main (README "Branch work in this repository"), staging only `openspec/changes/official-resale` (and `openspec/changes/payments-legal-compliance`, updated in the same PR); verify `openspec-checks.yml` passes and the PR merges

## 2. Proto (specification → BSR)

- [x] 2.1 Add `entity/v1/resale_listing.proto` with `ResaleListingId` and `ResaleListing` (design D9: id, ticket_id, price, fee, refund_amount, status LISTED/SOLD/WITHDRAWN/CANCELLED/EXPIRED, create_time, deadline_time, sold_time, refund_time) and doc comments from `components/entity/resale-listing`; verify `buf lint` and `buf format -d` pass
- [x] 2.2 Add `rpc/resale_listing/v1/resale_listing_service.proto` with `Create`, `Withdraw` and `List` (rpc-design skill; the caller is never named), with protovalidate on the ids; verify `buf lint` passes
- [x] 2.3 Add `bool resale_open` and `bool resale_available` to the fan's TicketType and `bool resale` to the Checkout, with doc comments saying no count is ever returned; verify `buf breaking` reports nothing
- [x] 2.4 Update the `AdmissionWindow` doc comment in `entity/v1/scanner.proto` to "from 3 hours before the start time" (design D11); verify `buf lint` passes
- [x] 2.5 Open the proto PR from a worktree, merge it, and cut the next minor Release; verify `buf-release.yml` succeeds and BSR has the version

## 3. Backend — schema and entities

- [x] 3.1 Write the Atlas migration that creates `resale_listings` and adds `ticket_types.resale_open_time` (design D8: columns, the partial unique index on `ticket_id WHERE status = 1`, the `(ticket_type_id, create_time) WHERE status = 1` index, grants), and mirror it in `rdb/schema/schema.sql`; verify `make lint-schema` and `TestMigrationGrants_IAMRoles` pass (full CRUD for `fan-api`, SELECT for `organizer-console-api`, none for `reception-api`)
- [x] 3.2 Add `entity.ResaleListing` with fee, refund amount, deadline, open, expired and free rules; verify one unit test per scenario of `components/entity/resale-listing` ("Round price", "Price that does not divide evenly", "Smallest price", "Event with an open time", "Event without an open time", "Before the deadline", "At the deadline", "Sold listing", "Never held", "Held by another fan", "Hold lapsed", "Being charged")
- [x] 3.3 Add the resale rules to `entity.TicketType` and `entity.Checkout` and the share-of-resold-tickets rule to `entity.Settlement`; verify one unit test per scenario of `components/entity/ticket-type` (resale requirements), `components/entity/checkout` ("Resale checkout long before the deadline", "Resale checkout just before the deadline", "Two listings of two fans", "The fan's own listing") and `components/entity/settlement` ("One of two tickets resold", "One of three tickets resold", "Last ticket resold")

- [x] 3.4 Count `admissionWindowLead` from the start time only in `internal/entity/scanner.go` (design D11); verify one unit test per scenario of `components/entity/scanner` "Admission window" ("Usual evening show" now opens at 16:00, "No open time", "Before the window", "Window closed", "No start time") and that the `usecase/ticket/admit` tests still pass

## 4. Backend — entity operations

- [x] 4.1 Declare and implement `ResaleListing.Create`, `Get`, `Withdraw`, `ListByUser`, `ListSoldUnrefunded`, `RecordRefund` in `rdb`; verify one contract test per scenario of each `components/entity/resale-listing/<operation>` spec against Postgres, including "Listed twice" and "Withdraw and hold at the same moment" run concurrently
- [x] 4.2 Implement `ResaleListing.SendSoldEmail` on the Postmark sender with `sold_email_send_time` set once (design D6); verify one contract test per scenario of `components/entity/resale-listing/send-sold-email` with the Postmark client faked
- [x] 4.3 Extend `TicketType.Get` and `TicketSale.ListByEvent` with the free resale count; verify the scenarios "Sold-out ticket type with listings" and "Sold-out sale with free listings" and that the existing contract tests still pass
- [x] 4.4 Extend `Checkout.GetOrCreateHeld`, `Commit` and `RevertCommit` for resale Checkouts and the resale open time (design D1, D3); verify one contract test per scenario of `components/entity/checkout/get-or-create-held` ("Hold resale listings, oldest first"), `commit` and `revert-commit` against Postgres, including "Two fans, last listing" run concurrently
- [x] 4.5 Extend `Order.Issue` to sell the listings, void their Tickets and give up the Settlement shares in the same transaction (design D4), and `Order.CommitRefund` to void only Issued Tickets and cancel Listed listings; verify one contract test per scenario of `components/entity/order/issue` and `components/entity/order/commit-refund` against Postgres
- [x] 4.6 Give `Order.CreateRefund` a purpose and the idempotency key `resale-listing-refund:<listing id>` (design D7); verify one contract test per scenario of `components/entity/order/create-refund` against the Stripe test API (or the recorded fixture the existing tests use)

## 5. Backend — usecases, handler and job

- [x] 5.1 Implement `ResaleListingUseCase.Create`, `Withdraw` and `List`; verify one unit test per scenario of `components/usecase/resale-listing/create`, `withdraw` and `list` with the operations mocked
- [x] 5.2 Implement `ResaleListingUseCase.RefundSold` (refund, then announce `ORDER.resale_listing_refunded`) and call it from `startCheckoutSweepers` after `IssueDueCheckouts`, and `NotificationUseCase.SendResaleSold` with its `ORDER.resale_listing_refunded` consumer in the event consumer (design D6); verify one unit test per scenario of `components/usecase/resale-listing/refund-sold` and `components/usecase/notification/send-resale-sold`
- [x] 5.3 Change `CheckoutUseCase.Start`, `OrderUseCase.Refund` and `TicketSaleUseCase.ListByEvent`; verify one unit test per scenario of `components/usecase/checkout/start`, `components/usecase/order/refund` and `components/usecase/ticket-sale/list-by-event`, and that their existing tests still pass
- [x] 5.4 Add `ResaleListingHandler` and map `resale_open`, `resale_available` and `resale` in the ticket sale and checkout handlers, wiring everything in `internal/di`; verify the handler tests for every scenario of `components/adapter/fan/api/rpc/resale-listing`, `ticket-sale` ("Resale without a count") and `checkout` ("Resale checkout started")
- [x] 5.5a Add the NACK `Consumer` `send-resale-sold` (stream `ORDER`, filter `ORDER.resale_listing_refunded`) in cloud-provisioning `k8s/namespaces/nats/base/jetstream/` (design D6); verify the PR merges and the consumer exists in prod (`nats consumer info ORDER send-resale-sold`, read-only) before the backend release
- [x] 5.5 Open the backend PR (OpenSpec-Change: official-resale) once BSR has 2.5; verify CI passes, merge, and verify in prod that the AtlasMigration status shows the migration applied and the fan-api rollout is healthy (read-only `kubectl` with `CLOUDSDK_ACTIVE_CONFIG_NAME=liverty-music`)

## 6. Frontend — fan app

- [x] 6.1 Event page ticket section: the 公式リセール block for a SoldOut or Ended TicketType with resale open; verify route unit tests for "Sold out with a resale ticket" and "Sold out, nothing listed" and that the existing ticket section tests still pass
- [x] 6.2 Checkout: the resale lines and sale period on the 特商法 final confirmation for a resale Checkout; verify a route unit test for "Resale final confirmation"
- [x] 6.3 Tickets screen: the 出品中 / リセール済み / 無効 states, the listing confirmation, withdrawal and refund display; verify route unit tests for every scenario of `components/infrastructure/fan/web/route/tickets` "List a ticket for official resale" and "A listed ticket can be withdrawn and shows its outcome", plus "Resold ticket"
- [x] 6.4 Terms of Service: add the official resale article in ja and en; verify a unit test for "Resale article present"
- [x] 6.5 Open the frontend PR (OpenSpec-Change: official-resale); verify CI passes, merge, and verify the release reaches prod

## 7. Production verification (Stripe test mode)

- [x] 7.1 Add `e2e/prod/resell-a-ticket.spec.ts` covering `stories/resell-a-ticket` on a test event with a 2-ticket first-come sale in Stripe test mode (sell out, list, buy from a second account, check void, new ticket, refund of 4500 of 5000 yen, payouts, withdraw, two fans for one listing); verify it passes against production
- [x] 7.2 Run the Stripe Sandbox E2E (`gh workflow run stripe-sandbox-e2e.yml`); verify it passes and the refund appears on the original charge in the Stripe test dashboard
