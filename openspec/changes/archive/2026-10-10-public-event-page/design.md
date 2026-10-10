## Context

See proposal.md for the motivation. The approach is shaped by these facts:

- **Concert detail is dashboard-only today.** The fan app opens a concert only as the dashboard's detail sheet. `/concerts/:id` resolves the id against the fan's followed-artist list and silently degrades when the concert is not there.
- **No single-event read exists.** The fan `ConcertService` exposes only list RPCs.
- **The fan Series mapping is minimal.** It carries only id, title, type and source URL, so the app cannot tell a first-party concert from a discovered one.
- **The entity operations already exist:**
  - `Concert.ListByIDs` returns concerts regardless of visibility.
  - `Series.Get` returns the first-party attributes and the cover Media.
  - `Concert.ListEventsBySeries` returns id, date and start time per Event.
- **Concert reads carry only part of the Series.** Every Concert read (`ListByIDs` and the fan lists) filled only the Series' title, type and source URL, so `Series.OrganizerID` was always nil on a Concert. Implementation adds the Series' `organizer_id`, `description`, `visibility` and `publish_state` to those reads, without the cover Media (a join) or the share token. The notification link (D9) and the dashboard card routing (D7) depend on this; `Get` and `ListBySeries` still replace the Series with the `Series.Get` result, which carries the cover.
- **Guests can already open every route.** The frontend `AuthHook` lets them through, and `data.auth === false` skips the wait for auth readiness.
- **The OIDC callback already supports a return path.** It honours `authService.takeReturnTo()` (built for involuntary re-auth) and calls `onboarding.finish()`. The post-signup dialog is armed through the `postSignupShown = 'pending'` flag on a sign-up flow.
- **fan-web is served by Caddy.** It uses `file_server` with `try_files {path} /index.html`, and `index.html` has no Open Graph tags.
- **fan-api runs two HTTP servers.**
  - The Connect server (`fan-api-svc:80`) is fully public.
  - The webhook server (`fan-api-webhook-svc:9090`) receives calls from external systems (Stripe, Zitadel); the public gateway routes only `/stripe-webhook` to it.
- **Rate limiting is a Connect interceptor.** It is keyed per IP for public RPCs, so a plain HTTP handler on the Connect server's mux is outside it.
- **No Kubernetes NetworkPolicy** restricts traffic between the frontend and backend namespaces.
  - Verified in prod on 2026-10-08 (task 1.2): from the `fan-web-app` Pod in `frontend`, `wget http://fan-api-svc.backend.svc.cluster.local:80/link-preview/events/<uuid>` returns 200 from fan-api v1.65.0. (`/healthz` is not a fan-api path and answers 401; the health check is the gRPC health service.) The `backend` namespace has no NetworkPolicy.
- **The backend layers** put handlers that receive calls and map entities to an output format in `internal/adapter/` (`rpc/` with `mapper/`, `webhook/`), and server wiring in `internal/infrastructure/server`.
- **Aurelia 2 has no production-ready server-side rendering** (as of 2026-10). The only option is the community package `aurelia2-ssr` v0.0.3.

## Goals / Non-Goals

**Goals:**
- A shareable `/events/:id` that renders without sign-in and gives crawlers full link-preview tags, with no new infrastructure.
- One read path that serves both the page and its link preview, so the two cannot disagree about which events have a page.

**Non-Goals:**
- The sale UI, inventory, checkout, post-purchase prompts (`first-come-ticket-sales`), and `?ref=` capture (`referral-attribution`).
- Showing the Organizer. The 特商法 seller details (name, address, contact) are shown in the purchase flow of `first-come-ticket-sales`, where the law requires them.
- UNLISTED share-token access. The pilot event is PUBLIC.
- Server-side rendering of the page body, generated Open Graph images, and an English link preview.
- Pages for discovered concerts.

## Decisions

### D1 — One page per Event, keyed by EventId

- The route is `/events/:id`, and `id` is the EventId, the same id a Concert carries.
- Sale, tickets, check-in and the sold-out trigger for resale are all per Event, so the page shows them without aggregating.
- The new-concert notification already links by EventId.
- Discovered concerts use the same id space, so a later extension keeps the URL.
- **Rejected: `/series/:id`.** Its link-preview card cannot name a date or venue, and every ticket state would need aggregating.

### D2 — Two read methods, each returning its own entity

**`ConcertUseCase.Get(eventId)` returns one Concert:**

1. `Concert.ListByIDs([id])`.
2. `Series.Get(series id)`.
3. Return NotFound unless the Series has an event page, using the new Series rule: first-party, PUBLIC, and PUBLISHED or CANCELLED.

**`ConcertUseCase.ListBySeries(seriesId)` returns the Series' Concerts:**

1. `Series.Get`, then the same event-page check.
2. `Concert.ListEventsBySeries` for the ids in date order.
3. `Concert.ListByIDs(ids)`, then reorder the Concerts to the ListEventsBySeries order, which also orders same-day shows by start time.

Both methods return the same NotFound on every miss, so a DRAFT or UNLISTED event's existence is not revealed.

- **Each method returns only its own entity, Concert.** Composing a page (the Concert plus its Series' dates) is the caller's job: the event screen and the link-preview handler each call both methods.
- **Rejected: one `GetEventPage` returning an aggregate.** It would put a screen concept into the usecase layer, and its name would not match what it returns.
- **No new entity operation.** A dedicated `Concert.Get` would duplicate `ListByIDs` with one id.
- **Rejected: extending the Concert visibility rule.** It would also add CANCELLED concerts to fan lists. The event-page rule stays separate from list visibility; lists still hide CANCELLED.

### D3 — RPC shape

- `ConcertService.Get(GetRequest{event_id})` returns `GetResponse{concert}`.
- `ConcertService.ListBySeries(ListBySeriesRequest{series_id})` returns `ListBySeriesResponse{repeated concerts}`.
- No entity message changes. The fan `SeriesToProto` additionally sets the existing optional fields `organizer_id`, `description`, `media`, `visibility` and `publish_state` when the Series has them. Admin and organizer reads already return the same shape, so the fan mapping stops being the exception. The share token has no proto field.
- The Media URLs for the fan are the same CDN URLs the organizer console already gets.
- The event screen calls `Get`, then `ListBySeries` with the returned Series id, without blocking navigation. A single-Event Series costs one extra small call; this is accepted for the cleaner contract.

### D4 — Link preview: Caddy `templates` + a public fan-api HTTP endpoint

- **`index.html`** gains:
  - Site-default `og:*` and `twitter:*` tags.
  - One comment placeholder, `<!--{{httpInclude (printf "/__link-preview%s" .OriginalReq.URL.Path)}}-->`.
- **Caddy** enables `templates { between "<!--{{" "}}-->" }` only for `@event path /events/*`:
  - `.OriginalReq` is used because `try_files` rewrites the path to `/index.html`.
  - `handle /__link-preview/*` rewrites to `/link-preview/*` and reverse-proxies to `fan-api-svc.backend.svc.cluster.local:80` inside the cluster.
  - Hashed assets and other routes are untouched; elsewhere the comment is inert.
- **fan-api** gains a plain HTTP handler `GET /link-preview/events/{id}` on the Connect server's mux:
  - It calls `ConcertUseCase.Get` and `ConcertUseCase.ListBySeries`, and renders the tag block with Go `html/template`, so every value is escaped.
  - It always returns 200. On NotFound or any error it returns an empty body, so the site-default tags in `index.html` stand.
  - Responses are cached in memory for 60 s per id.
  - The site-default tags are written after the placeholder, and crawlers take the first `og:*` occurrence, so the event tags win when present.
- **Endpoint placement:**
  - The path is public through the existing catch-all route. That is harmless, because it returns only data `ConcertService.Get` already returns publicly.
  - It sits on the Connect server rather than the webhook server, which stays dedicated to calls from external systems.
  - The per-IP rate limit is a Connect interceptor and does not apply. So all crawler traffic, which reaches fan-api from Caddy's Pod IP, is not throttled as one client. Task 7.1 verifies this.
- **Code placement (no new layer):**
  - `internal/adapter/linkpreview/` holds the handler and the function that turns a Concert and its Series' Concerts into the tag block, with the template beside it.
  - It mirrors `internal/adapter/rpc/` with `mapper/`: the handler only calls usecases and maps entities to an output format, which is HTML tags here instead of proto.
  - The mux registration lives with the other server wiring in `internal/infrastructure/server`.
- **Tag content:**
  - Japanese, with dates formatted in Asia/Tokyo.
  - `og:url` is the canonical `https://liverty-music.app/events/{id}`, so `?ref=` and other query parameters are dropped.
  - `og:image` is the cover's `large` WebP variant, or the static brand image `/og-default.png` (1200×630) when there is no cover.
- **Rejected alternatives:**
  - Aurelia SSR, which is not production-ready.
  - Build-time prerender, because events are created at runtime.
  - User-agent sniffing with headless rendering, which Google deprecates and which needs a pod.
  - A prerender SaaS (cost, lock-in).
  - A Cloudflare Worker, which would add a second edge layer on top of Cloud DNS delegation.
  - A Go handler serving `/events/*` HTML through a cross-namespace HTTPRoute, which couples fan-api to the frontend's `index.html` on every deploy.
  - Building the tags in Caddy templates from `ConcertService.Get` JSON, where escaping HTML correctly is hard and fragile.
  - Placing the endpoint on the internal webhook server, which would mix in a second role for no security gain since the data is public.

- **Spike result (task 1.1, 2026-10-08, `caddy:2-alpine` as pinned in the fan Dockerfile, stub upstream):**

  | Upstream answer | Plain `reverse_proxy` | With the settings below |
  |---|---|---|
  | 200 with tags | page, event tags first | page, event tags first |
  | 200, empty body | page, site defaults | page, site defaults |
  | 404 | **500, empty page** | page, site defaults |
  | 500 | **500, empty page** | page, site defaults |
  | no response (10 s) | page after **10 s** | page after 1 s, site defaults |
  | upstream down | **500, empty page** | page, site defaults |

  - `httpInclude` fails the whole response on any non-2xx sub-response or dial error, so the hardening is required, not optional.
  - Strip the prefix with `handle_path` and rewrite to `/link-preview{path}`: `uri strip_prefix /__` leaves a request target without a leading `/` (`link-preview/events/<id>`), which fan-api's mux would not match (found while verifying task 11.2).
  - The `@event` matcher must test the original path (`expression {http.request.orig_uri.path}.startsWith("/events/")`), because `try_files` has already rewritten the path to `/index.html` when `templates` runs. On other routes the placeholder comment is served unchanged and is inert.
  - Resulting settings for task 11.2:

    ```caddyfile
    handle_path /__link-preview/* {
    	rewrite * /link-preview{path}
    	reverse_proxy fan-api-svc.backend.svc.cluster.local:80 {
    		transport http {
    			dial_timeout 500ms
    			response_header_timeout 1s
    		}
    		@notok status 1xx 3xx 4xx 5xx
    		handle_response @notok {
    			respond "" 200
    		}
    	}
    }
    handle_errors {
    	@preview path /__link-preview/*
    	respond @preview "" 200
    }
    ```

### D5 — WebP `og:image`, verified before adding JPEG

- X and Facebook render WebP previews despite Facebook's documentation. LINE is unverified.
- The rollout task checks LINE Page Poker, the Facebook Sharing Debugger and a real X post.
- A JPEG og variant in `ProcessMedia` (plus a backfill) is added only if a platform fails. That would be a follow-up change, so the specs here state no image format.

- **Rollout check (task 12.2), 2026-10-08**, event `01a06666-04fe-7b59-ab7b-f6bf330c6a32` (series「テスト1」, cover served as `large.webp`):

  | Platform | Card | WebP cover |
  |---|---|---|
  | LINE (app, shared in a chat) | shown | shown |
  | Slack (unfurl) | 「テスト1 \| UVERworld」, 「2026年9月25日(金) テスト」, Liverty Music | shown |
  | Facebook Sharing Debugger | skipped (owner's decision) | — |
  | X (real post) | skipped (owner's decision) | — |

  - LINE Page Poker no longer resolves (`poker.line.naver.jp`), so LINE was checked in the app itself.
  - Crawler user agents (`facebookexternalhit`, `Twitterbot`, `Line`, `Slackbot`) all receive the event tags first, with `og:url` stripped of `?ref=`.
  - **Conclusion:** the WebP `large` variant is enough for the pilot. The JPEG og variant follow-up is not opened; revisit it only if a Facebook or X share shows no image.

### D6 — Sign-up from the event page reuses return-to

- Starting sign-up on the event page stores `returnTo = /events/:id` and marks the flow as `origin: event-page` in the OIDC state, beside the existing sign-up flow marker.
- On callback, the existing path runs: user provisioning, the guest follow migration and `onboarding.finish()`. It then navigates to `takeReturnTo()`.
- When the origin is `event-page`, the callback does not set `postSignupShown`, so neither the celebration overlay nor the dialog appears later on the dashboard.
- `first-come-ticket-sales` owns the post-purchase permission and install prompt.

### D7 — Dashboard routing and badges

- **Card routing:** a card whose Series carries an organizer emits `event-selected` like any card, but the dashboard handles it by router navigation to `/events/:id` instead of opening the sheet.
- **Back navigation:** going back uses the existing `ConcertHighway.scrollOffset` restore.
- **Purchased badge:** for first-party cards, the badge comes from `TicketService.GetMyTickets`, counting Issued tickets per event, instead of the journey map.
- **Badge caching:** the tickets call is made once per dashboard load and cached like the journey map. On failure the cards show no badge, which matches the journey behaviour.

### D8 — Date tabs up to 4 Events

- A Series with 2–4 Events shows the dates as tabs.
- A Series with more shows an "other dates" list under the main content.
- 4 fits a 360 px wide viewport with "M/D (曜)" labels at the 44 px tap-target minimum.
- Tabs are links (`<a href="/events/<id>">`), so each date is shareable and back navigation works.

### D9 — Notification link

- `NotifyNewConcerts` already loads Concerts with their Series.
- When the earliest matched Concert's Series has an organizer, the link becomes `/events/<id>`; otherwise it stays `/concerts/<id>`.
- The service worker opens `data.url` unchanged.

## Risks / Trade-offs

- **[Risk] Caddy `httpInclude` errors may fail the whole response, which would blank `/events/*` for users during an API outage.** → Mitigation:
  - A spike (task 1.1) verifies Caddy's behaviour on a 5xx response and on a timeout.
  - The endpoint never returns non-200.
  - If the spike shows a hard failure on a timeout, the reverse proxy gets a 1 s `response_header_timeout` plus `handle_errors` returning an empty 200.
- **[Risk] Every `/events/*` HTML request now makes an internal call.** → Mitigation: there is a 60 s in-memory cache, the HTML is `no-cache` but small, and pilot traffic is low.
- **[Risk] Crawler caches keep a stale card after an event is cancelled or edited** (about 7 days on X and about 1 day on Facebook and LINE). → Mitigation: the organizer runbook tells them to use the Facebook Sharing Debugger and LINE Page Poker to refresh. This is accepted.
- **[Trade-off] Cancelled events keep a public page while lists hide them.** Shared links keep explaining what happened. A cancelled page reveals nothing that was not already public.
- **[Trade-off] The ticket section shows only purchased tickets until `first-come-ticket-sales` ships.** The page is still useful for sharing and following before sales open.

## Migration Plan

1. **specification:** `ConcertService.Get` and `SeriesEvent`, then a Release and BSR generation.
2. **backend:** in one PR,
   - the Get and ListBySeries usecases and handlers,
   - the fan Series mapping,
   - the link-preview endpoint,
   - the notification link.
3. **frontend:** in one PR,
   - the `event` route,
   - dashboard routing and badges,
   - the bottom-nav mapping,
   - sign-up return,
   - the `index.html` defaults,
   - the Caddyfile.
4. Promote to prod, then verify link previews on LINE, Facebook and X.

Rollback: revert the frontend release. The new RPC and the extra Series fields are additive and harmless to older clients.
