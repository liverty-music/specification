## 1. Specification: proto comment

- [ ] 1.1 Rewrite the `Publish` doc comment in `proto/liverty_music/rpc/organizer/series/v1/series_service.proto` as design D5 says (claim only a discovered Event; a slot held by another Organizer's or another of this Organizer's series' Event fails; drop "is suppressed"), and verify `buf lint` and `buf format -d` report nothing and the specification PR's `buf breaking` passes without a skip label

## 2. Backend: entity operation (components/entity/series/publish-events)

- [ ] 2.1 Change the slot switch of `SeriesRepository.PublishEvents` to D1's order (cancelled, this series, any first-party holder refused with "the event's slot is held by another series' event", otherwise claim), reduce `claimEventQuery`'s comment to the discovered case, and update the `PublishEvents` doc in `internal/entity/series.go`; verify `go build ./...`
- [ ] 2.2 Add the contract test `@spec components/entity/series/publish-events "Slot of another Series of the same Organizer"` to `internal/infrastructure/database/rdb/series_events_repo_test.go`: a PUBLISHED UNLISTED Event of Series A with a seat type, a stock and a sale, and a DRAFT Event of Series B (same Organizer) at its slot. Assert FailedPrecondition, the draft still DRAFT, and the Event still in A with A's visibility, stock and sale. Keep the existing scenarios ("Claim a discovered event", "Another Organizer's slot", "Cancelled slot", "Suppressed slot" and the rest) passing; verify with `make test` in backend

## 3. Backend: usecase (components/usecase/series/publish)

- [ ] 3.1 Add the unit test `@spec components/usecase/series/publish "Own other concert holds the slot"` to `internal/usecase/series_lifecycle_uc_test.go`: `PublishEvents` mocked to return FailedPrecondition; assert Publish returns it and nothing is announced and no share token is set. The usecase code needs no change unless the test shows otherwise. Verify with `make test`
- [ ] 3.2 Open the backend PR citing this change, merge it, release it (GitHub Release, then the prod pin bump), and verify the prod fan-api and organizer API roll out the new version (`kubectl rollout status` read-only, or the ArgoCD app's synced image)

## 4. Frontend: organizer console (components/infrastructure/organizer/web/route/concert, .../event)

- [ ] 4.1 Confirm that the concert editor stops a draft with a blank title, no performer, or a date without venue or date from reaching 公開する (design D3's assumption). If one of them can reach it, record it in design.md D3 and narrow the message's condition. Verify by reading the editor's validation and, where it is unclear, by trying it in a local build
- [ ] 4.2 In `organizer/concert/concert-route.ts` and `organizer/event/event-route.ts`, map FailedPrecondition from publish to the new snackbar key (ja text in design D3, en equivalent), with no retry, and reload the dates. Keep `event.publishFailed` with its current retry for other errors. Add unit tests `@spec components/infrastructure/organizer/web/route/concert "Date already used by another concert"` and `@spec components/infrastructure/organizer/web/route/event "Publish refused for a used slot"`, and verify with `make check` in frontend
- [ ] 4.3 Check the members' guide chapter 公演をつくって公開する (`organizer/guide/guide.html`) and `specification/docs/organizer-console-story-map.md`. If they describe publishing, add that a date on a venue, date and start time already used by another concert or a cancelled date cannot be published, and how to fix it. Verify `test/organizer/guide.spec.ts` passes
- [ ] 4.4 Update the WARNING in `frontend/docs/prod-e2e-fixtures.md` "Creating the Events": a fixture on a used slot is now refused, not taken over. Drop the backend#737 takeover description and keep the advice to give each fixture a free slot. Verify by reading the rendered section
- [ ] 4.5 Open the frontend PR citing this change and merge it after task 3.2

## 5. Production verification and cleanup

- [ ] 5.1 After 3.2 and 4.5, as the e2e-test Organizer's test member in production, create a draft concert with a date on the venue, date and start time of an existing published fixture, and press 公開する on the event page and on the concert page. Verify each shows the slot message with no 再試行, the date stays 下書き, and `ConcertService.Get` for the fixture's Event id still returns the fixture's Series. Then remove the draft with 公演を中止 (a draft is removed)
- [ ] 5.2 Retire the Series moved on 2026-10-30 (design D4: "E2E Sale 1030", "E2E Referral 1030", "E2E Resale 1030b" and the emptied "E2E Resale"), following `docs/prod-e2e-fixtures.md` "Retiring used Events" and skipping any Event `.auth/prod-e2e.env` names. Verify the organizer `SeriesService.List` no longer lists them
- [ ] 5.3 Comment on backend#737 with the decision and the merged PRs, and close it
