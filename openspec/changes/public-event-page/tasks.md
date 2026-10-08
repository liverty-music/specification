## 1. Spikes (frontend Caddy, cloud-provisioning)

- [ ] 1.1 Spike the Caddy `templates` + `httpInclude` behaviour for design D4 against a local reverse-proxy stub. Test the stub returning 200, 404, 500, no response (timeout) and an empty body, check whether the page HTML is still served in each case, and record the result and the resulting Caddyfile settings (`response_header_timeout`, `handle_errors`) in design.md D4
- [ ] 1.2 Confirm in prod that a Pod in the `frontend` namespace reaches `fan-api-svc.backend.svc.cluster.local:80` (`kubectl exec` with a `curl` to `/healthz`). Record the result in design.md Context

## 2. Proto (specification → BSR)

- [ ] 2.1 Add `rpc Get(GetRequest) returns (GetResponse)` (`event_id` required, response `concert`) and `rpc ListBySeries(ListBySeriesRequest) returns (ListBySeriesResponse)` (`series_id` required, response `repeated concerts`) to the fan `ConcertService`, with doc comments listing NotFound and InvalidArgument and no entity message change. Verify `buf lint`, `buf format -d` and `buf breaking` pass with no breaking change
- [ ] 2.2 Open the specification PR, merge it, cut the Release, and verify the `buf-release.yml` run succeeds and the BSR packages carry `ConcertService.Get` and `ConcertService.ListBySeries`

## 3. Entity rule (components/entity/series)

- [ ] 3.1 Add the event-page rule to the backend Series entity as a guard ("has an event page"). Verify a unit test per scenario of "Which series' events have an event page" passes: Published public series, Cancelled public series, Unlisted series, Draft series, Discovered series

## 4. Usecases (components/usecase/concert/get, components/usecase/concert/list-by-series)

- [ ] 4.1 Implement `ConcertUseCase.Get` per design D2 with Concert.ListByIDs and Series.Get. Verify unit tests pass with the operations mocked for Published public concert, Cancelled series, Unknown id, Unlisted series, Discovered concert and Store unavailable
- [ ] 4.2 Implement `ConcertUseCase.ListBySeries` per design D2 with Series.Get, Concert.ListEventsBySeries and Concert.ListByIDs, in ListEventsBySeries order. Verify unit tests pass with the operations mocked for Two-day run, Same day, two shows, Unlisted series, Discovered series and Store unavailable

## 5. Fan boundary (components/adapter/fan/api/rpc/concert)

- [ ] 5.1 Add the `Get` and `ListBySeries` handlers as public procedures (no auth requirement) calling the usecases, and set the existing `organizer_id`, `description`, `media`, `visibility` and `publish_state` in the fan `SeriesToProto` (design D3). Verify handler tests pass for Guest opens an event page, Guest lists the dates of a series, Event page without an id, First-party concert in a list and Discovered concert in a list, and that the existing concert handler tests still pass

## 6. Notification link (components/usecase/notification/notify-new-concerts)

- [ ] 6.1 Build `/events/<id>` for an earliest concert whose Series has an organizer, and keep `/concerts/<id>` otherwise (design D9). Verify the new unit test "First-party concert links to its event page" passes and the existing link scenarios still pass

## 7. Link preview endpoint (components/infrastructure/fan/web/global/link-preview, backend part)

- [ ] 7.1 Add `internal/adapter/linkpreview` with the handler for `GET /link-preview/events/{id}` and its tag-building function, registered on the fan-api Connect server's mux (design D4). It calls `ConcertUseCase.Get` and `ListBySeries`, renders the escaped tag block with `html/template` per "Event page links carry the event's preview", always returns 200, returns an empty body on NotFound or error, and caches for 60 s per id. Verify unit tests cover Shared on X (exact title and description text, JST times, "全N公演"), Link with a referral code (`og:url` without the query), Cancelled event, Unlisted event link (empty body), Event read fails (200, empty body), Series cancelled (cache expiry within 60 s) and an HTML-escaping case. Also verify a test showing that repeated requests from one IP are not rate-limited
- [ ] 7.2 Open the backend PR (after 2.2) covering groups 3–7, get `make check` and CI green, merge, cut a release, and verify the prod pin moved and `ConcertService.Get` answers in prod for a published PUBLIC event

## 8. Event page (components/infrastructure/fan/web/route/event)

- [ ] 8.1 Add the `events/:id` route with `data.auth === false`, loading through `ConcertService.Get` and then `ConcertService.ListBySeries` without blocking navigation. Render the content of "What the event page shows" with i18n keys for every label (ja and en), dates and times in the display language, organizer text as entered and the Google Maps link. Verify component tests pass for Guest opens a shared link, Event without a cover image, Start time not announced and English display language
- [ ] 8.2 Add the performer follow controls using the existing follow store (guest and signed-in). Verify a component test for Guest follows the artist
- [ ] 8.3 Add the date tabs (2–4 Events) and the "other dates" list (more than 4) as links (design D8). Verify component tests for Two-day run and Six-stop tour, and a Storybook visual baseline at 360 px with 4 tabs
- [ ] 8.4 Add the ticket section showing purchased Issued tickets from `TicketService.GetMyTickets`, with a link to Tickets. Verify tests for Fan holding two tickets and Voided tickets are not counted
- [ ] 8.5 Add the cancelled banner (中止, refund notice, link to the artist's other concerts), the ended state (Japan-time date compare) and the not-found / retry views. Verify tests for Shared link after cancellation, Day after the show, Unlisted event and Network failure
- [ ] 8.6 Add the share control (Web Share API with copy-link fallback) and add-to-calendar (an `.ics` download using the date and times in Japan time). Verify a component test that the shared URL is the canonical `/events/<id>` and that the `.ics` carries the event's start

## 9. Sign-up return (route/event + components/infrastructure/fan/web/global/post-signup-dialog)

- [ ] 9.1 Provide the event page's sign-up entry: store `returnTo=/events/:id` and an `origin: event-page` marker in the OIDC state, and have the auth callback skip arming `postSignupShown` for that origin (design D6). Verify tests for Guest signs up to buy (lands on the event page, follow migrated, onboarding complete), Guest signs up while buying (no celebration or dialog later on the Dashboard) and Sign-up from the landing page (unchanged)

## 10. Dashboard and navigation (components/infrastructure/fan/web/route/dashboard, global/bottom-nav-bar)

- [ ] 10.1 Route first-party card selection to `/events/:id` in the timetable and the All Nearby list, and keep the sheet for discovered concerts (design D7). Verify tests for Open detail from dashboard (discovered), First-party concert opens its event page and Back from the event page (timetable restored at the left date)
- [ ] 10.2 Show the purchased badge on first-party cards from one `GetMyTickets` call per dashboard load, and no journey badge on them. Verify tests for Tracked concert, Concert without a journey, Statuses cannot be loaded, Purchased first-party concert and First-party concert not purchased
- [ ] 10.3 Map `/events/:id` to the Home section in the route configuration. Verify the bottom-nav test for Event page highlights Home and that the existing tab tests pass

## 11. Link preview in the fan web (components/infrastructure/fan/web/global/link-preview, frontend part)

- [ ] 11.1 Add the site-default `og:*` and `twitter:*` tags and the `httpInclude` placeholder to `index.html`, and add the `/og-default.png` (1200×630) brand image to `public/`. Verify `npm run build` keeps the placeholder comment in `dist/index.html`, and `verify:build-templates` passes
- [ ] 11.2 Add the Caddyfile `@event path /events/*` templates block, the `/__link-preview/*` rewrite and reverse proxy to `fan-api-svc` `/link-preview/*`, and the error handling settled in 1.1, with `Cache-Control: no-cache` on `/events/*` HTML. Verify with a local container that `/events/<id>` returns the event tags first when the backend answers, and the site defaults when the backend is down, with the page still loading
- [ ] 11.3 Open the frontend PR (after 2.2) covering groups 8–11, get `make check` and CI green, merge, and verify the prod pin moved

## 12. Story and production check (stories/open-a-shared-event-link)

- [ ] 12.1 Add the E2E test for the story: Guest from a social post, Unlisted series, Guest follows then signs up, Follower taps the notification (deep-link URL asserted), and Link opened after cancellation. Verify it passes against prod with a test Organizer's PUBLIC and UNLISTED Series
- [ ] 12.2 In prod, check the preview of a published event with LINE Page Poker, the Facebook Sharing Debugger and a real X post (design D5). Record whether each platform shows the WebP cover in design.md D5, and if any fails, open the JPEG og variant follow-up
- [ ] 12.3 Update issue liverty-music/specification#1074: mark public-event-page shipped and link the PRs
