## 1. Proto and plan (specification)

- [x] 1.1 Add `RESALE_ENTRY_LOST_REASON_LISTING_CANCELLED = 5` to `ResaleEntryLostReason` in `proto/liverty_music/entity/v1/resale_entry.proto`, with a comment saying the win was charged and the charge refunded because a listing allocated to it was cancelled (design D3); verify `make check` passes, open the proto PR, merge once `CI Success` passes, cut the Release and confirm `buf-release.yml` succeeds (`gh run list --repo liverty-music/specification --workflow buf-release.yml --limit 3`)

## 2. Schema and entity (backend)

- [x] 2.1 Add an Atlas migration widening `chk_resale_entries_lost_reason` to 1..5 and updating the `resale_entries.lost_reason` column comment, and update `schema.sql`; verify `atlas migrate hash`, `scripts/check-migration-drift.sh`, `make lint-schema` and a `migrationtest` that stores a Lost entry with the new reason
- [x] 2.2 Upgrade the generated schema package, add the `ResaleEntryLostReasonListingCancelled` constant and its pb mapping (design D3); verify the pb mapping test covers the new value

## 3. Entity operation (components/entity/resale-entry/revert-win)

- [x] 3.1 `RevertWin` accepts the lost reasons "concert cancelled" and "listing cancelled"; the listings need no change, since a Cancelled listing is never free for a draw (design D4); verify one contract test per scenario of `entity/resale-entry/revert-win`, including "Listing cancelled", which checks that the Listed listing is free for the next draw and the Cancelled one is not

## 4. Issue a won resale entry (components/usecase/order/issue)

- [x] 4.1 In the `capture` step, check that the event is still PUBLISHED and, when it is not, revert the win with "concert cancelled" without charging (design D1); verify the scenario "Concert cancelled before the charge" with the operations mocked, and that a replayed workflow after a capture does not check again
- [x] 4.2 Make `sellResaleListings` return `entity.ErrResaleListingCancelled` when an allocated listing is Cancelled, (design D2); verify a contract test where the reselling fan's Order is refunded before the sell, and one where the refund and the sell run concurrently and exactly one of them wins
- [x] 4.3 On that error, refund the whole charge with `Order.CreateRefund` for the Order's own refund (retrying Unavailable for up to 24 hours and telling an admin), then revert the win with "listing cancelled" (design D2); verify the scenario "Listing cancelled after the charge" with the operations mocked, and that a replay refunds once
- [x] 4.4 Run a resale story on the Stripe test API (`STRIPE_INTEGRATION_TEST=1`): a Won entry whose reselling fan's Order is refunded by an admin cancellation between the capture and the issue ends Lost with "listing cancelled", and the winner's charge is refunded at Stripe; verify it passes

## 5. Release and email (components/usecase/order/release-card-authorization, components/usecase/notification/send-resale-entry-ended)

- [x] 5.1 `StartResaleEntryWorkflow` releases the card authorization of a win reverted with "concert cancelled" and not of one reverted with "listing cancelled"; verify the scenarios "Win reverted for a cancelled concert" and "Win reverted after a refund"
- [x] 5.2 The ended email and push for "listing cancelled" say the win was cancelled because the ticket could no longer be sold and the charge is refunded to the card, in Japanese and English; verify the scenario "Listing cancelled" of `usecase/notification/send-resale-entry-ended`

## 6. Release and production check

- [x] 6.1 Merge the backend PR, cut the release once the push-path image is built, and confirm in prod (read-only) that the AtlasMigration is applied, the backend deployments run the new release, and `gh workflow run stripe-sandbox-e2e.yml` succeeds
