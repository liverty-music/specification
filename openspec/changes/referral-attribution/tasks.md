## 1. Specification — main-spec Purposes and the plan PR

- [ ] 1.1 Edit the main spec Purposes directly (proposal "(Purpose)"), and verify `openspec validate --specs` and `python3 scripts/check-spec-layout.py` pass:
  - `components/entity/checkout`: add `Checkout ||--o| Referral : "was started from"` to the erDiagram;
  - `components/entity/lottery-entry`: add `LotteryEntry ||--o| Referral : "was started from"` to the erDiagram;
  - `components/usecase/checkout/start` and `components/usecase/lottery-entry/start`: add "and records the referral code it was started with";
  - `components/usecase/ticket-sale/list-own-by-event`: add "and the event's purchases per referral code";
  - `components/infrastructure/organizer/web/route/event`: add "and its purchases per referral code" to the Sales tab clause.
- [ ] 1.2 Open the plan PR from a worktree cut from origin/main (README "Branch work in this repository"), staging only `openspec/changes/referral-attribution` and the main specs edited in 1.1; verify `openspec-checks.yml` passes and the PR merges

## 2. Proto (specification → BSR)

- [ ] 2.1 Add `entity/v1/referral.proto` with `ReferralCode { string value = 1 [(buf.validate.field).string = {min_len: 1, max_len: 32, pattern: "^[a-z0-9-]+$"}] }` and a doc comment from `components/entity/referral` (design D2); verify `buf lint` and `buf format -d` pass
- [ ] 2.2 Add `optional entity.v1.ReferralCode referral_code = 3` to `rpc/checkout/v1` and `rpc/lottery_entry/v1` `StartRequest`, with doc comments stating that a malformed code fails with INVALID_ARGUMENT and that it is recorded while the Checkout is Held or the entry is a Draft (design D5); verify `buf lint` passes and `buf breaking` reports nothing
- [ ] 2.3 Add `ReferralCodeStats` next to `LotteryEntryStats` in `rpc/organizer/ticket_sale/v1/ticket_sale_service.proto`, and `repeated ReferralCodeStats referral_code_stats = 3` to `ListByEventResponse`, with doc comments (absent code = direct, Paid Orders only, amount in whole yen 税込) and the `ListByEvent` rpc comment updated (design D5); verify `buf lint` and `buf breaking` pass
- [ ] 2.4 Open the proto PR from a worktree, merge it, and cut Release v0.86.0 (or the next minor); verify `buf-release.yml` succeeds and BSR has the version

## 3. Backend (one PR after 2.4)

- [ ] 3.1 Write the Atlas migration after `20261013002947` that creates `referrals` (design D1: columns, `chk_referrals_id_uuidv7`, `chk_referrals_one_source`, `chk_referrals_code`, the two partial unique indexes, `ON DELETE CASCADE`, comments), and mirror it in `rdb/schema/schema.sql`; verify `make lint-schema` and `TestMigrationGrants_IAMRoles` pass, the last proving `referrals` is SELECT-only for `organizer-console-api`, inaccessible to `reception-api` and full CRUD for `fan-api` (design D6)
- [ ] 3.2 Add `entity.ReferralCode` with `Validate()`, `entity.Referral`, `entity.ReferralSource` (exactly one of Checkout and LotteryEntry) and the open-source guard in `internal/entity/referral.go`; verify one unit test per scenario of `components/entity/referral` passes ("Code from a link", "Empty or too long", "Other characters", "One code whatever the case in links", "Referral of a checkout", "Two sources", "Held checkout", "Draft entry", "Confirmed source")
- [ ] 3.3 Declare `ReferralRepository.Record` and implement it in `rdb.ReferralRepository` with the source row lock of design D3; verify one contract test per scenario of `components/entity/referral/record` passes against Postgres ("First code", "Same code again", "Last link wins", "Confirmed source keeps its code", "Confirmed source without a code", "Concurrent records", "Unknown source"), plus the `entity/referral` scenarios "Abandoned checkout removed with its concert" (through `Concert.DeleteAndSuppress`) and "Lottery entry kept after its user is deleted" (through `User.Delete`)
- [ ] 3.4 Declare `ReferralRepository.ListStatsByEvent` and implement the query of design D4; verify one contract test per scenario of `components/entity/referral/list-stats-by-event` passes against Postgres ("Two codes and direct purchases", "Lottery win counted once its Order exists", "Refunded order excluded", "Abandoned checkout not counted", "Other events not counted", "No purchases")
- [ ] 3.5 Give `CheckoutUseCase.Start` and `LotteryEntryUseCase.Start` the optional code and call `Referral.Record` after `GetOrCreateHeld` / `GetOrCreateDraft` (design D3), wiring the repository in `internal/di`; verify the unit tests with mocked operations pass for `usecase/checkout/start` "Record the referral code the checkout started with" (all five scenarios) and `usecase/lottery-entry/start` "Record the referral code the entry started with" (all four scenarios), and that the existing Start tests still pass
- [ ] 3.6 Change `TicketSaleUseCase.ListOwnByEvent` to return the sales with `Referral.ListStatsByEvent` (design D5); verify the unit tests pass for every scenario of `usecase/ticket-sale/list-own-by-event`, including "Purchases per referral code"
- [ ] 3.7 Map `referral_code` in `CheckoutHandler.Start` and `LotteryEntryHandler.Start`, and `referral_code_stats` in `OrganizerTicketSaleHandler.ListByEvent`; verify the handler tests pass for `adapter/fan/api/rpc/checkout` and `adapter/fan/api/rpc/lottery-entry` "Malformed referral code" and "Referral code passed on", and for a ListByEvent response that carries a direct group without a code
- [ ] 3.8 Open the backend PR (OpenSpec-Change: referral-attribution) once BSR has 2.4; verify CI passes, merge, and verify in prod that the AtlasMigration status shows the new migration applied and the fan-api and organizer-console-api rollouts are healthy (read-only `kubectl` with `CLOUDSDK_ACTIVE_CONFIG_NAME=liverty-music`)

## 4. Frontend — fan app

- [ ] 4.1 Add `src/adapter/storage/referral-storage.ts` (key `referral`, value `{code, seriesId, expiresAt}`, every access in try/catch, expired or malformed entries dropped on load; design D7); verify unit tests for save, load, expiry at exactly 7 days, malformed JSON and a storage that throws
- [ ] 4.2 Capture `ref` on the Event page after the event loads (design D7); verify unit tests for `route/event` "A referral link's code is kept on the device": "Guest opens a referral link", "Uppercase code", "Newer link replaces the code", "Malformed code ignored", "Unknown event", and a functional Playwright test for "Code survives sign-up" against the mocked backend
- [ ] 4.3 Send the kept code from the checkout and lottery entry routes through `checkoutClient.start` / `entryClient.start` when the Series matches; verify route unit tests for `route/checkout` ("Purchase three days after the link", "Code expired", "Another Series", "Direct visit") and `route/lottery-entry` ("Entry from a referral link", "Another Series", "Code expired")
- [ ] 4.4 Confirm that sign-out leaves `referral` in place and that og:url and the share URL still carry no query; verify a unit test on the sign-out cleanup and the existing `e2e/prod/open-a-shared-event-link.guest.spec.ts` og:url assertion

## 5. Frontend — organizer console

- [ ] 5.1 Map `referralCodeStats` in `organizer/services/ticket-sale-client.ts` and `organizer/model/sale-model.ts`, and render the 紹介コード別の購入 section in `sales-tab.html` with ja and en strings (design D8); verify component tests for `route/event` "The Sales tab shows purchases per referral code": "Two codes and direct purchases", "Sale with no purchase yet", "Event without a sale"

## 6. Frontend — storage names without `liverty` (design D9)

- [ ] 6.1 Rename every name in the design D9 table and update the tests that spell them (e2e `analytics-opt-out`, `onboarding-flow`, `page-help-sheet-webkit`, `beam-*`; unit `dashboard-route`, `auth-callback-route`, `checkout-route`, `consent-service`, `consent-route`, `console-context`, `auth-hook`); verify `grep -rniE "liverty[-:_]" src shared organizer reception e2e test` finds no storage name, postMessage type, cache, database or tag, `make check` passes, and the tests annotated for the MODIFIED scenarios of `global/post-signup-dialog`, `global/page-help`, `global/fab-menu`, `route/my-artists` and `stories/merge-guest-data-on-signup` pass with the new names
- [ ] 6.2 Delete the legacy migrations instead of renaming them: `migrateFromV1()` and the v1 keys in `consent-storage.ts`, `migrateStorageKeys()` and its legacy keys in `storage-keys.ts`, the `onboardingStep` migration in `onboarding-storage.ts`, and their tests; verify `make check` passes and no code reads a removed key
- [ ] 6.3 Replace the "do not rename" comment in `reception/services/scanner-key-store.ts` with a pointer to design D9, and verify by unit tests that a missing `wallet` database leads the tickets screen to offer この端末で入場する (no automatic registration while the server has a key) and a missing `scanner` key leads the reception page to the other-device message
- [ ] 6.4 Before deploying 6.1, list production Scanners that are InUse for events that have not ended (read-only, db-proxy runbook `cloud-provisioning/docs/runbooks/cloud-sql-access.md`); verify the count is recorded here, and after the deploy reissue each with 取り消して再発行 on the event's Reception tab, or record that there are none
- [ ] 6.5 After the deploy, on the owner's and the tester's phones open the tickets screen and confirm この端末で入場する once; verify the entry QR code shows again (design D9)

- [ ] 6.6 Add `before_send` to the PostHog init config with `src/lib/analytics/strip-own-url-query.ts`, which removes `search` and `hash` from every URL value on the app's origin in `properties`, `$set` and `$set_once` (design D11); verify unit tests for `global/analytics` "Analytics events carry no query string of the app's own addresses": "Event on a referral link", "First address of the visit", "Another site's address", and that "Analytics off" still sends nothing (existing opt-out test); `make check` passes

## 7. Frontend — Privacy Policy

- [ ] 7.1 Add the purchase-records and purchase-route lines to section 2 and the referral purpose to section 3 of `legal.privacy` in `src/locales/ja/translation.json` and `src/locales/en/translation.json`, and update the revision date (design D10); verify the legal-document test covering "Collected data and purposes are stated" checks both new categories in ja and en
- [ ] 7.2 Open the frontend PR with groups 4–7 (OpenSpec-Change: referral-attribution) once BSR has 2.4; verify CI passes, merge, and verify the prod rollout of the new frontend version is healthy

## 8. Production verification

- [ ] 8.1 Add `e2e/prod/attribute-a-purchase-to-a-referral-link.authenticated.spec.ts` in the pattern of `buy-tickets-first-come.authenticated.spec.ts`: open `/events/<E2E_SALE_EVENT_ID>?ref=e2e-member-a`, buy 1 ticket with the Stripe test card, then read organizer `TicketSaleService.ListByEvent` with `E2E_ORGANIZER_TOKEN` and assert the `e2e-member-a` row grew by 1 Order; a second purchase after opening `?ref=e2e-member-b` counts under `e2e-member-b` ("Last link wins"). Verify it passes on production for the story scenarios "Guest from a member's link buys after signing up" (signed-in variant; the sign-up leg is covered by 4.2) and "Last link wins"; "Another tour is not attributed" and "Link older than 7 days" are covered by 4.3
- [ ] 8.2 Read `referrals` joined to `orders` for the 8.1 purchases on production (read-only, db-proxy runbook); verify one row per source with the expected code and no row for a purchase without a code, and record the result here
- [ ] 8.3 Run `gh workflow run stripe-sandbox-e2e.yml --repo liverty-music/backend`; verify the run succeeds, showing the payment path is unchanged
- [ ] 8.4 Open the event's Sales tab in the production organizer console; verify the 紹介コード別の購入 section shows the 8.1 rows and 直接（コードなし） last
