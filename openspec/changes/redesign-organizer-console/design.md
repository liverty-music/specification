## Context

See proposal.md - Why. The UX plan agreed with the owner (claims, mocks and sketches, 2026-10-10) is the source of the screens; the decisions below override it where they differ.

Current state, verified in the code on 2026-10-10 (frontend `main` at `e0f6c3d`):

- **Shell and routes.** `frontend/organizer/organizer-shell/organizer-shell.ts:23-87` is one flat route list (`concerts`, `concerts/new`, `concerts/edit/:seriesId`, `lottery/configure/:eventId`, `lottery/status/:phaseId`, `reception-links/:eventId`, `welcome`, `denied`, `auth/callback`); the comment at `:46-51` admits the lottery editor is reachable only by deep link. `organizer-shell.html` is a bare `<au-viewport>`. No organizer file calls `IAuthService.signOut` (`shared/services/auth-service.ts:348`), so there is no sign-out.
- **Publish without confirmation.** `concerts/concerts-route.ts:209-224` publishes on one click; the class comment at `:156-157` says Publish and Cancel are confirmed, but only Cancel has a two-step reveal (`concerts-route.html:79-133`).
- **Venue field.** The editor asks for a raw place id (`concert-editor/concert-editor-route.html:134-139`, placeholder `ChIJ…`), and `concert-editor-route.ts:230` hydrates every event with `placeId: ''`, so each save resends the venue by name only. The read side cannot do better today: `entity/v1/venue.proto:9-21` has no place id although the Venue entity has one (`specs/components/entity/venue`), while `EventDraft.place_id` exists on write (`rpc/organizer/series/v1/series_service.proto`, `EventDraft`).
- **Save feedback.** `concert-editor-route.ts:283-315` sets `saveError` on failure and shows nothing on success.
- **Time zone.** `concert-editor/concert-form.ts:92-105` builds event times in the browser's time zone; `lottery-sale-editor/lottery-sale-form.ts` does the same for the window; `lottery-status/lottery-status-route.ts:35` uses `toLocaleString()`. A Japan-time formatter already exists for the reception screens (`shared/lib/reception/jst-format.ts`).
- **No i18n.** `organizer/main.ts:147-162` registers "NO i18n machinery"; every string is English. The fan app's set-up is `src/main.ts:166-190` (`I18nConfiguration`, `fallbackLng: 'ja'`, detection querystring → localStorage → navigator).
- **Styles.** `organizer/styles/main.css` (245 lines) copies a subset of the fan tokens with the fan app's dark navy surface. The fan tokens have `--md-easing-emphasized-accelerate: cubic-bezier(0.3, 0.8, 0.15, 1)` at `src/styles/tokens.css:146` (wrong), state layers focus and pressed 12 % at `:251-252`, and only `long2`/`long4` of the long durations.
- **Fan primitives.** `<loading-spinner>` is registered at `src/main.ts:291` and used only at `src/routes/verify-callback/verify-callback-route.html:6`. `<snack-bar>` lives in `src/components/snack-bar/` (default 2500 ms, `snack.ts:29`; `Infinity` supported, `snack-bar.ts:62-68`) and is mounted in `src/app-shell.html:28`.
- **Backend reads the console can use.** `OrganizerService.Get`, `ArtistService.List` (the represented Artists; `rpc/organizer/artist/v1`), `PayoutAccountService.Get` (account status plus `onboarding_url` while not active), `SeriesService.List` (each authored Series with its dates as Concerts, which carry their event ids, and each Artist once) and `RegenerateShareUrl` (returns the new share token, not a URL (`backend/internal/adapter/rpc/organizer_series_handler.go:250-256`); the Series' token is "never shown on reads", `specs/components/entity/series`). After `unify-ticket-sales`: `TicketSaleService.ListByEvent(event_id)` with entry stats per TicketType (`usecase/ticket-sale/list-own-by-event`: entries, requested tickets, Won entries, Won tickets, Lost entries) and `SetVerificationRequirement`.
- **Map catalog.** The backend already calls Places Text Search with Application Default Credentials (`backend/internal/infrastructure/maps/google/client.go:27,90`, `SearchPlace` returns one best match). No browser Maps key exists.
- **M3 values**, fetched today from AndroidX sources: `StateTokens.kt` hover 0.08, focus 0.10, pressed 0.10, dragged 0.16 (no selected value); `MotionTokens.kt` durations 50-1000 ms and easings standard (0.2,0,0,1), standard-accelerate (0.3,0,1,1), standard-decelerate (0,0,0,1), emphasized-accelerate (0.3,0,0.8,0.15), emphasized-decelerate (0.05,0.7,0.1,1); `SnackbarHost.kt` Short 4000 ms, Long 10000 ms, Indefinite. Window size classes (compact < 600, medium 600-839, expanded 840-1199 dp) and the 48 dp target come from the brief's check of the Android Developers docs; not re-fetched here.

Constraints: bundle isolation (`make verify-bundle-isolation`, `lint-boundaries`: only `shared/` crosses between `src/`, `admin/`, `organizer/`, `reception/`); CUBE CSS with the repository's stylelint plugin; no users, dev stopped.

## Goals / Non-Goals

**Goals:**
- One console structure that the three preceding changes plug into, usable at 360 px and at 1920 px.
- Share code with the fan app only where both apps need the same behavior.

**Non-Goals:**
- The admin console shell (from `refactor-shared-ui-design-system`); follow-up issue (task 0.6).
- The first-come sale editor and its states (`route/ticket-sale-editor`, shipped by `first-come-ticket-sales`); this change gives it its Sales tab entries, to start and to change the event's first-come sale.
- The reception screen staff use at the door and the reception guide (`ticket-wallet-and-checkin`, `isolate-venue-reception`).
- Changing a lottery sale once its window has opened (the server refuses it, `usecase/ticket-sale/set-window` and `usecase/ticket-type/update`), renaming a sale, and cancelling a sale (no RPC). Refunds, settlement statements, a pre-publish preview and a sales checklist (story-map items without an RPC; listed in the plan).
- Changing the fan app's colors, type or components beyond the shared tokens, the snack bar move and the spinner replacement.
- A `SeriesService.Get`: `List` is enough for an Organizer's small catalog (the plan's decision).

## Decisions

### D1 — Routes: every screen has one parent, under its Organizer and Artist

Amended after the owner's production walk-through (2026-10-13): addresses carry the Organizer id and, below a represented Artist, the Artist id (owner decision: "URLには ID を入れる"; collection names per AIP-122, plural English words, no one-letter abbreviations). `{o}` is the Organizer id, `{a}` an Artist id.

| Address | Screen | Parent (breadcrumb) | Destination |
|---|---|---|---|
| `/organizers/{o}` | Home | — | ホーム |
| `/organizers/{o}/artists/{a}/series` | Concerts (公演) of one represented Artist | — | 公演 |
| `/organizers/{o}/artists/{a}/series/new` | Concert editor (new; the Artist is the first performer) | Concerts | 公演 |
| `/organizers/{o}/artists/{a}/series/{series}` | Concert | Concerts | 公演 |
| `.../series/{series}/edit` | Concert editor | Concert | 公演 |
| `.../series/{series}/events/{event}/ticket-sales` (default tab) | Event, 販売 tab | Concert | 公演 |
| `.../series/{series}/events/{event}/scanners` | Event, 受付 tab | Concert | 公演 |
| `.../events/{event}/ticket-sales/new?method=lottery` | Lottery sale editor (new) | Event | 公演 |
| `.../events/{event}/ticket-sales/new?method=first-come` | First-come sale editor (`route/ticket-sale-editor`), new | Event | 公演 |
| `.../events/{event}/ticket-sales/{sale}/edit` | The sale's editor (lottery before it opens, or first-come) | Event | 公演 |
| `/organizers/{o}/settings` | Settings | — | 設定 |
| `/`, and any unknown address | opens `/organizers/{own id}` | — | — |
| `denied`, `auth/callback` | unchanged | — | — |

- **Path words are the entities' names (2026-10-13).** Collection segments use the entity names (`entity/series`, `entity/event`, `entity/ticket-sale`, `entity/scanner`), in the AIP-122 pattern of alternating collection and id. The first draft used `concerts/{seriesId}`, but a Concert is one Event with its performers (`entity/concert`), so a concert-under-concert path named the same thing twice. The UI keeps its words (公演 for a Series, 日程 for an Event, 販売, 受付). `new` and `edit` are not resources: they are the web convention for the create and edit forms (Rails routing: `/photos/new`, `/photos/:id/edit`); AIP covers APIs, not screens. `settings` is a screen name.
- **Depth.** Rails advises nesting one level deep with shallow member routes; the full hierarchy is kept here so the address carries the Artist and the Series for the breadcrumb, and a co-headlined concert's parent is decided by the address (owner, 2026-10-13).
- **One login reaches one Organizer.** The backend resolves the caller's Organizer from the token's single login-scope org (`backend/internal/infrastructure/auth/org_scoped.go:109-145`, `OrganizerUseCase.ResolveCaller`), and no organizer-facing RPC takes an organizer id. The `{o}` segment is therefore checked, not used: the shell compares it with `OrganizerService.Get().organizer.id`; another id shows a page saying the address belongs to another Organizer, with サインアウト to switch accounts. `/` and an unknown address open the caller's own Home. The backend stays the authority.
- **A concert is reachable under each represented Artist who performs in it (owner decision, 2026-10-13).** A Series may have several performers, each represented by the caller's Organizer (`SeriesDraft.artist_ids`, `backend/internal/usecase/series_uc.go:193-209`), so a co-headlined concert has one address per represented performer; both open the same concert, and its breadcrumb follows the Artist in the address. A concert opened under an Artist who does not perform in it is not found. Concerts of an Artist lists the concerts that Artist performs in, filtered on the client from `SeriesService.List` (`Concert.artist_ids`); `SeriesService.List` has no filter and needs none at this catalog size.
- **Choosing the Artist.** The 公演 destination opens the Artist in the current address; on Home and Settings it opens the Artist last opened on this device, else the first represented Artist by name. When the Organizer represents two or more Artists, the top app bar shows the current Artist as a menu button listing them (M3 menu); with one it shows the name only. An Organizer that represents no Artist yet gets a 公演 page saying so and that Liverty Music adds Artists on request.
- **Org pinning for sign-in is separate.** `?org_id` / `?org` and the saved `liverty:organizer:org_id` (`frontend/organizer/services/org-handle.ts:23-77`) choose the Zitadel org's login policy at sign-in and are unchanged; the backend builds the invitation's return address with it (`backend/internal/infrastructure/zitadel/organizer_provisioner.go:416`). The path carries the Organizer id, which is not the Zitadel org id, so the two stay separate. Story `sign-in-as-organizer` and `hosted-login` said the org is bound "NOT to a URL parameter", which read literally forbids this designed hint; their intent, that a URL value never grants an org, holds because the token's org decides (`org_scoped.go`, `org-enforcement.ts`). This change rewords both (MODIFIED deltas): the `org_id` is a hint for the login policy and grants nothing (owner, 2026-10-13).
- Removed: `home`, `concerts/...` and `settings` without the organizer prefix, together with the earlier removals (`lottery/configure/:eventId`, `lottery/status/:phaseId`, `scanners/:eventId`, `welcome`, `concerts/edit/:seriesId`). No redirects: there are no users, and the fallback opens Home.
- **Why the event id stays under the concert:** the breadcrumb needs the concert, and `SeriesService.List` is the only read; a flat `events/:eventId` would need a reverse lookup across all concerts.
- Tabs are child routes so a tab is a shareable address (spec "Reception tab address"). The tab bar is an M3 primary tabs component driving the router.
- Every console path is built by one module (`organizer/model/concert-model.ts` `paths`) from the current Organizer and Artist; templates do not hard-code paths (today 9 places do, listed in task 9.6).
- One breadcrumb component in the shell renders the trail on medium and wider windows; on compact windows the top app bar shows a back arrow to the parent instead (M3 app bar: "A back arrow, which returns to the previous screen"). The parents' names (a concert title, an event date) are known only after the screen's read, so each screen below a destination sets its trail through an `IBreadcrumbs` service once it has them, as catalog keys, Japan-time days or names, so a language switch updates it; a navigation whose screen sets none clears it. The destination marked in the navigation is read from the address.

### D2 — Data per screen, no new read RPC

| Screen | Reads |
|---|---|
| Home | `SeriesService.List`, `PayoutAccountService.Get`, and for each published event starting within 7 days the scanner list of `rename-reception-to-scanner` (an Organizer has a handful of such events; calls run in parallel) |
| Shell | `OrganizerService.Get` (the Organizer id checked against the address, its name) and `ArtistService.List` (the Artist menu) |
| Concerts, Concert | `SeriesService.List`, filtered to the Artist in the address; sale state per event from `TicketSaleService.ListByEvent` for published events only, lazily per visible event |
| Event | `SeriesService.List` (find the event), `TicketSaleService.ListByEvent(event_id)`, `OrganizerService.Get` (business details prerequisite), scanner list |
| Settings | `OrganizerService.Get`, `ArtistService.List`, `PayoutAccountService.Get` (re-read on `visibilitychange` to visible) |

- **Sale state on lists** costs one `TicketSaleService.ListByEvent` per published event. With the current catalog (tens of events) this is acceptable; the plan's alternative (a sale summary on the `SeriesService` List response) is the follow-up if lists get slow. Recorded, not built.
- Countdown and "open/closed" are computed on the client from the sale's times and the clock, refreshed every 60 s; the server stays the source of truth for whether an entry is accepted.

### D3 — Responsive layout: window class for navigation, container class for lists

- Navigation: one CSS media query at `width >= 600px` switches the M3 navigation bar (bottom, 80 px high, 3 items) to the M3 navigation rail (80 px wide). Expanded windows (≥ 840 px) keep the rail rather than a navigation drawer: three destinations do not need a drawer (M3 recommends a drawer for 5+ destinations or expanded labels).
- Lists: the list component sets `container-type: inline-size`; `@container (width >= 840px)` renders a `<table>` with the same data; narrower, it renders an M3 list (D18; cards until 2026-10-13). Both are rendered from one template branch per mode, not by restyling a table into cards, so screen readers get real table semantics on wide screens and a list on narrow ones.
- Every interactive component sets `min-block-size` and `min-inline-size: 48px` on its target (a pseudo-element extends small icons).
- The page body has a max inline size of 1200 px on expanded windows so lines stay readable.

### D4 — Console-local components under `frontend/organizer/ui`

Navigation bar/rail, top app bar with account menu, breadcrumb, button (filled, tonal, outlined, text; pending state), icon button, dialog (native `<dialog>` with `showModal()`: focus trap, Escape and focus return come from the platform), tabs, card list/table, description list, stat tile, status badge (color + text), text/select/datetime/money/venue fields with an error slot, copy field, prerequisite callout, sticky action bar for editors (on compact windows the save button sits above the navigation bar).

- **Why local:** the fan app has different shapes and density, and the plan counted 2 users of `state-placeholder` and 1 of `loading-spinner`; sharing them would couple two release cycles for little saving.
- The unsaved-changes guard is a router `canUnload` hook on the editors plus `beforeunload` while dirty.
- Pending buttons keep their width by reserving the label width; repeat presses are ignored by the button component, not by each screen.

### D5 — Feedback and motion tokens

- `frontend/shared/styles/m3-sys.css` defines `--md-sys-state-{hover,focus,pressed,dragged}-opacity` (0.08/0.10/0.10/0.16), `--md-sys-motion-duration-*` (16 values) and `--md-sys-motion-easing-*` (5 values) from the AndroidX files above, and a `@media (prefers-reduced-motion: reduce)` block that sets every duration to 0 ms. Both apps import it; `src/styles/tokens.css` keeps its existing `--md-*` names as aliases to the shared ones, so no fan component changes. `--md-state-selected: 12%` stays fan-local because M3 publishes no selected opacity in `StateTokens.kt`.
- State layers are a `::before` overlay of `currentColor` at the token opacity.
- Snackbar host: one instance in the organizer shell. Durations: 4000 ms without action, 10000 ms with a non-retry action, `Infinity` for a retryable error (the Compose Indefinite case). A new snack replaces the shown one (M3 shows one at a time; the fan component stacks, so the host passes a "replace" option).
- Copy: `navigator.clipboard.writeText`, icon swaps to check for 2000 ms, `aria-live` announcement.
- Page transitions: same-document View Transitions (`document.startViewTransition`) around router navigation with a shared-axis X slide (medium2 300 ms, emphasized easing); skipped when the API is missing or motion is reduced. New scanner rows: `@starting-style` with emphasized-decelerate, medium4 400 ms. Tab indicator: `transform` transition, medium2.

### D6 — Style: shared role names, console values, fixed type scale

- Console tokens live in `frontend/organizer/styles/tokens.css` with the fan role names (`--md-color-surface`, `on-surface`, `primary`, …; the fan app's names, not `--md-sys-color-*`) and values from `light-dark()`, with `color-scheme: light dark` on `:root`. Brand magenta `oklch(65% 0.28 350deg)` stays the `primary` role; status colors (success, warning, error, neutral) are separate roles, always beside a text label.
- Type scale fixed in px from M3 `TypeScaleTokens.kt` (body-large 16/24, body-medium 14/20 default, label-large 14/20, title-medium 16/24, title-large 22/28, headline-small 24/32); font stack `"Hiragino Sans", "Noto Sans JP", "Yu Gothic UI", system-ui, sans-serif`; `font-variant-numeric: tabular-nums` on numbers.
- **This amends Decision 2 of `refactor-shared-ui-design-system`** (fluid `clamp()` scales everywhere) for the console: an operator compares numbers across windows, and M3 adapts layout, not text size, across window classes.
- Contrast is checked in tests by computing role pairs (D10).

### D7 — Language, time and money

- `@aurelia/i18n` registered in `organizer/main.ts` like `src/main.ts:166-190`, with `detection.order: ['localStorage', 'navigator']`, `fallbackLng: 'ja'`, `supportedLngs: ['ja','en']`, and the same `lng: undefined` override. Catalogs in `frontend/organizer/locales/{ja,en}/translation.json`. Operators have no User row, so the choice is per device only (the console origin has its own localStorage). A locale-changed subscriber sets `document.documentElement.lang`.
- Dates: `Intl.DateTimeFormat(locale, { timeZone: 'Asia/Tokyo', … })` followed by "JST". Entry: `<input type="datetime-local">` / `date` / `time` values are read as wall-clock parts and converted with a fixed +09:00 offset (Japan has no daylight saving time), replacing `new Date(y, m, d, h, min)` in `concert-form.ts` and `lottery-sale-form.ts`. The reception helper `shared/lib/reception/jst-format.ts` stays for the reception app.
- Money: English uses `Intl.NumberFormat('en', { style: 'currency', currency: 'JPY' })` (`¥6,500`); Japanese formats the number with `Intl.NumberFormat('ja')` and appends 円 from the catalog (`6,500円`), because the `ja` currency style gives `￥6,500`, which is not how Japanese ticket prices are written.
- UI copy keeps 受付 for scanners and the entity-grounded vocabulary (`i18n` "Two-Layer Vocabulary Model" applies by analogy; the console catalog has its own `entity.*` namespace).

### D8 — Shared code with the fan app

| Shared item | Path | Fan effect |
|---|---|---|
| M3 system tokens | `frontend/shared/styles/m3-sys.css` | emphasized-accelerate fixed; focus and pressed state layers 12 % → 10 % |
| Snack bar | `frontend/shared/ui/snack-bar/` (moved from `src/components/snack-bar/`) | none: same element, same events, fan default 2500 ms kept |
| Circular progress indicator | `frontend/shared/ui/circular-progress/` | replaces `<loading-spinner>` on the verification callback screen |

- `<loading-spinner>` and its stories are deleted and its registration at `src/main.ts:291` removed.
- `shared/ui` imports nothing from `src/`, `organizer/` or `admin/`; `lint-boundaries` and `verify-bundle-isolation` enforce it.

### D9 — Venue search through the backend

- New `VenueService.Search(text) → repeated VenueCandidate {place_id, name, address}` (`rpc/organizer/venue/v1/venue_service.proto`; planned as SeriesService.SearchVenues, shipped as its own service); `VenueUseCase.Search` validates the text and calls `Venue.SearchPlaces`, implemented on the existing Google client with `places:searchText`, `pageSize: 5`, `languageCode: ja`, `regionCode: JP`, field mask `places.id,places.displayName,places.formattedAddress`.
- **A new interface for the map catalog, not `entity.VenuePlaceSearcher`.** `Venue.SearchPlaces` and `Venue.GetPlace` are declared on a new interface implemented only by `infrastructure/maps/google`. `VenuePlaceSearcher` (`backend/internal/entity/venue.go:47`, one best match) is also implemented by MusicBrainz (`infrastructure/music/musicbrainz/place_searcher.go`) for discovered concerts, which has no candidate list or place details to offer; widening it would force stub methods there.
- ~~The field searches on an explicit action (search button or Enter).~~ Replaced on 2026-10-13 (owner's walk-through: an operator expects candidates while typing) by **search as you type with Places Autocomplete (New)**:
  - The field searches 500 ms after the operator stops typing, once the trimmed text has at least 3 characters when it contains a Japanese character (hiragana, katakana or kanji) or at least 5 characters otherwise (owner decision: 「武道館」 must search at 3; Latin prefixes such as "Zepp" match too broadly below 5). Google suggests waiting for "the first three or four characters" (Place Autocomplete (New), cost optimization). Only the answer to the latest text is shown; an earlier answer arriving late is dropped.
  - The field is an ARIA combobox: the candidates are a listbox, arrow keys move, Enter picks, Escape closes.
  - `Venue.SearchPlaces` moves from `places:searchText` to `places:autocomplete` (`input`, `languageCode: ja`, `regionCode: jp`, no `includedPrimaryTypes`; at most 5 `placePrediction`s; name from `structuredFormat.mainText`, address from `structuredFormat.secondaryText`). No type filter: it matches the primary type only and allows five types, and a live house's primary type may be `bar` or `night_club`. The RPC (`VenueService.Search`, `VenueCandidate`) does not change; only `VenueCandidate.address`'s doc comment, which says "formatted address", now gets the prediction's secondary text (shorter, without the postal code).
  - **No session token.** A session ends only with a Place Details call; the backend calls Details only for a place not yet stored, at save time, possibly for several picks, and `GetPlace`'s field mask (with `displayName`, a Pro field) would bill the session's terminating call at Enterprise + Atmosphere (session-pricing page). Per-request billing: Autocomplete Requests, 10,000 free per month, then USD 2.83 per 1,000 (pricing page, 2026-10-13), cheaper per call than today's Text Search Pro (5,000 free, USD 32 per 1,000).
  - **Attribution.** Candidates shown without a map need Google Maps attribution "within the same visual container" (Places API policies); the candidate list ends with the text "Google Maps" (`translate="no"`), which the policy allows when the logo is not used. The current list lacks it.
- `Venue` gains an optional `place_id` on reads, so the editor resends the place of an unchanged row (spec "An unchanged venue is kept on save"). Today an authored event carries no venue on the wire: since `split-concert-from-event` the `SeriesService` responses go through `mapper.EventToProto` (`backend/internal/adapter/rpc/mapper/concert.go:100`), which sets `Event.venue` only when the Event carries one, and the authored read selects only `venue_id` for draft and published events (`backend/internal/infrastructure/database/rdb/series_repo.go:106,117`). That is why every reload empties the field. The fix is in the read: `Series.GetAuthored` (and `ListOwn` through it) joins `venues` and fills the Event's Venue (id, name, place id), and `VenueToProto` sets `place_id`.
- **A picked place is required (owner decision, 2026-10-10).** `EventDraft.place_id` becomes required in the proto, and `usecase/series/create` rejects an event without one. The operator never sees or types a place id: the editor sends the id of the candidate the operator picked from `VenueService.Search` (spec `route/concert-editor` "The venue is found by search"). The required field is the API's guarantee that every saved venue came from a pick. Until the console's venue field ships (task 6.8), the current editor's raw place id field is the only way to satisfy it; the owner accepted that gap (2026-10-11). A typed name alone used to create a Venue keyed by name with no admin area (`seriesDraftToInputs` never sets one), so same-named halls in different cities merged into one Venue, and new Venues had no coordinates, so location-based fan lists missed them.
- **A published or cancelled date needs no place id (2026-10-13).** `EventDraft.place_id` drops its protovalidate `required`, and `usecase/series/update` requires a place id only for new and DRAFT events. A PUBLISHED or CANCELLED date's venue still cannot change (story `publish-an-organizer-concert` "Venue cannot move after publish"): it counts as unchanged when the listed venue name matches and no place id is given or its Venue has none, and the editor resends the date's listed venue name. Without this, a date published before venues were picked has no place id, every request that resends it fails protovalidate, and the whole concert can no longer be corrected. An earlier draft of this decision stopped reading the venue of such dates; it contradicted that story and was dropped. Whether such dates exist in production was not checked (no Cloud SQL IAM user for the operator yet).
- **New Venue from the catalog's place.** When no Venue holds the picked place id, `Venue.GetPlace` reads the place with Places Details (`GET places/{id}`, field mask `id,displayName,location,addressComponents`, `languageCode: ja`); the admin area is the ISO 3166-2 code of the `administrative_area_level_1` component (the existing prefecture-name mapping in `internal/infrastructure/geo` covers JP). One Details call per new venue; the search already paid for the pick.
- **Rejected — keep the typed name when nothing matches:** it is the path that produced merged and location-less Venues. A venue the catalog does not know is not expected for the pilot; if one appears, the fix is to add it to the map catalog, not to accept free text.
- **Rejected — Maps JavaScript Places Autocomplete in the browser:** a new browser API key to provision and restrict, a third-party script and CSP entries in the console, for an action the backend can already serve with its existing credentials.
- **Cost:** see the search-as-you-type bullet above; at the expected volume every SKU stays within its free monthly usage (inferred, not checked against billing).

### D9a — Cover preview until the processed image replaces it

- Today the editor clears `coverImageUrl` after SetCoverImage and never reads again (`frontend/organizer/concert-editor/concert-editor-route.ts:347-350`), so the processing note stays until a reload. The backend keeps the previous cover image on the Series until the processor replaces it (`SeriesImageUseCase.Process` → `SeriesImage.ReplaceCover`), so a save before processing re-hydrates the editor with the previous cover's URL.
- After SetCoverImage the editor re-reads the concert (the existing `SeriesService.List` read) every 3 s for up to 60 s and swaps to the processed image once the Series' cover image id equals the uploaded one. While the returned cover image id differs, `hydrate` keeps the local preview. After 60 s the note says processing is taking longer and the next open shows the result.
- **Rejected — a SeriesImage status RPC:** one more read surface for a few uploads a month; the authored read already carries the cover image id.

### D10 — Testing approach

- Components and screens: Vitest + `@aurelia/testing` per scenario, with the Connect clients mocked.
- Layout and motion: Playwright functional tests (`e2e/functional`, existing `page.route` mocking and `support/auth-mocks.ts`) at 390 × 844 and 1280 × 800, including `prefers-reduced-motion` and `prefers-color-scheme` emulation.
- Contrast: a unit test computes the contrast of every role pair in both themes from the token file.
- Story: a Playwright functional test with mocked RPCs for both widths, plus one production walk-through by the owner (passkey sign-in cannot be automated) on an UNLISTED test concert whose performer has no followers, so publishing notifies no one.

### D11 — Spec handling of in-flight changes

- `route/scanners` (added by `ticket-wallet-and-checkin` as `route/reception-links`, renamed by `rename-reception-to-scanner`) is written as a REMOVED delta here, with the requirement names of the main spec (task 0.3).
- `route/lottery-sale-editor` (moved by `unify-ticket-sales`) keeps its path in this change. Once `unify-ticket-sales` and `first-come-ticket-sales` are both archived, the lottery editor and the first-come `route/ticket-sale-editor` are one screen family; merging the two main specs into `route/ticket-sale-editor` is a main-spec move done directly with a mapping table (task 8.1), not a delta. It waits until this change archives, because this change holds a delta on `route/lottery-sale-editor` that would lose its target.
- Publish and cancel are written as acting on an event or on a concert's dates together (D14). `restructure-event-publishing` puts Publish and Cancel on the concert list; this change removes that requirement from `route/concerts` (D14), so that change archives first and task 0.2 checks the wording once it has.

### D12 — What this change takes over from `refactor-shared-ui-design-system`

| Its requirement / decision | Here |
|---|---|
| `organizer-shell` "Console persistent navigation with no dead-end screens" | Superseded by `organizer-shell` "Persistent navigation around every screen" and "No screen is reachable only by its address" |
| `admin-shell` (same requirement for admin) | Not taken over; follow-up issue (task 0.6) |
| `ui-primitives` "Shared reusable UI primitives" | Superseded and narrowed: only the snack bar and the circular progress indicator are shared (D8); other primitives are console-local (D4) |
| `ui-primitives` "Responsive and accessible primitives" | Superseded for the console by `action-feedback` (48 px targets, focus) and `design-tokens` (contrast) |
| `design-tokens` "Single source of design tokens" | Superseded and narrowed: state, motion and easing tokens are single-source (fan `design-tokens` "State and motion tokens are shared with the organizer console"); color, type and shape values stay per app under shared role names |
| Decision 1 (no `@material/web`, M3 as design language) | Kept |
| Decision 2 (fluid scales win) | Amended for the console (D6) |
| Decision 3 (`registerSharedUi` for all three apps) | Not taken: two shared elements are registered where used |
| Decision 4 (shared console app-shell for admin and organizer) | Organizer only (D1, D4) |

The owner decides whether that change is deleted or archived as superseded (task 0.5).

### D13 — Editing a sale from the Sales tab

- **Why the Sales tab edits sales (owner decision, 2026-10-12):** there is no RPC to cancel or delete a sale, so without an edit entry a mistyped price or window cannot be fixed, and the first-come editor's changes after the start would be reachable only by typing its address. Every RPC already ships: `TicketSaleService.SetWindow` (a lottery until its window opens, a first-come sale at any time) and `TicketTypeService.Update` (a lottery until its window opens; a first-come sale under the price lock and the sold-plus-held floor).
- A first-come sale's 編集 opens the existing first-come editor, which already starts or changes the event's first-come sale; a lottery's 編集 opens the lottery editor in a change mode (the name is shown, not editable: no RPC renames a sale).
- **Two calls, no transaction.** The lottery editor saves the window first and the TicketType second, skipping a call whose values did not change. When the second call fails, the editor stays open with what was saved kept, says which part was not saved, and offers 再試行 in the snackbar.
- The Sales tab disables 編集 from the lottery's start time by the client clock; the server's FailedPrecondition stays the authority (spec "Sale opened while editing").

### D14 — Publishing and cancelling: the concert page for the concert, the event page for one date

- **Why not one date at a time only:** Publish notifies followers once per performer per publish, carrying every date it added (`usecase/series/publish` after `restructure-event-publishing`). Publishing a four-date tour from four event pages would notify followers four times. The concert page therefore publishes the draft dates the operator chooses in one action, and its dialog names them and says followers are notified once. The same page cancels the whole concert in one action (one cancellation announcement).
- **Why the event page keeps its own:** a single additional date, or one cancelled date, is a per-date job, and the Sales and Reception tabs point to 公開する when a date is still a draft. Its dialog says it publishes this date alone and points to the concert page for several.
- **Why not on the concerts list (owner decision, 2026-10-13):** the list is for finding a concert and seeing its state; an action on a row makes a notification one mis-tap away and hides which dates go out. `restructure-event-publishing`'s "Publish while a concert has draft dates" is REMOVED in `route/concerts`.
- Home's draft item already opens the concert page, so the first publish of a new concert is Home → concert page → 公開する.
- **Visibility** is a concert attribute fixed by the first publish, so it is chosen in the concert editor as two options with their effects (followers notified or share link only), and shown on the concert page (spec `route/concert-editor` "Visibility is chosen before publishing"). The editor had no visibility field, so no UNLISTED concert could be made in the console.

### D15 — Corrections after the owner's production walk-through (2026-10-13)

The first walk-through of v1.89.0 stopped on defects that the unit, story and functional suites had passed. Their causes, verified in the code, and the decisions D16-D21 that answer them:

| Defect seen | Cause | Decision |
|---|---|---|
| The top bar said "Liverty Organizer" | A name coined in implementation (`organizer/locales/*/translation.json` `app.logoMark`/`app.logoSub`) | D20 |
| 登録を続ける on Settings unreadable | A page's `@scope (settings-route)` rule for `.label` also matched the `.label` span inside `<console-button>`: an unbounded scope with a generic class name | D16 |
| Business detail labels, the language check mark and the concert type stayed English after switching to Japanese | View-model getters returned `i18n.tr()` results, which do not follow a language switch (69 `tr()` calls in 11 view-model files) | D17 |
| The type options were unreadable in dark mode | The native `<option>` picker ignores the console's tokens; no story opened the picker | D16 |
| A concert card had both a whole-card link and a 開く button | Not M3: "In a single-action list, the entire list item performs one action" and "Can't have secondary nested actions" (M3 Lists) | D18 |
| The time field showed AM/PM and minute-by-minute | `<input type="time">` formats by the device's locale and no attribute forces 24 h (MDN) | D19 |
| The share link was a bare token with no fan page behind it | `RegenerateShareUrl` returns the raw token (`organizer_series_handler.go:250-256`) and no fan route or RPC reads it (`SeriesRepository.GetByUnlistedToken` has no caller) | D21 |
| 登録を続ける opened Stripe with no word of what happens there | The external hand-off was built from the spec text alone, without walking the story | D18 (Settings) |
| No candidates while typing a venue | D9's explicit search | D9 |
| Saving an existing concert kept the editor open; the new date had no venue or times | Spec "Save gives feedback and keeps the operator in place"; no default for a new row | D19 |

### D16 — Console components are encapsulated in Shadow DOM

- Each custom element in `frontend/organizer/ui` renders into a shadow root (`@useShadowDOM()`), so no page style can reach inside it, and its own styles cannot reach out. The fan app stays in light DOM with `@scope`; the console differs because its pages compose many small generic components inside forms, where name clashes such as `.label` are likely.
- Shared rules that every component needs (state layer, touch target, focus ring, visually hidden) are one stylesheet passed to every shadow root through Aurelia's `StyleConfiguration.shadowDOM({ sharedStyles })`. Tokens are custom properties and inherit into shadow roots unchanged.
- Native form controls stay inside the component that labels them, so `<label for>` and the form's own submission keep working; the field components expose their value through `@bindable` and events, not by reaching into the shadow root.
- Page (route) styles stay in light DOM under `@scope (<route-element>)` and SHALL use class names that do not repeat a component's part names; a stylelint rule is not available for this, so the full-screen checks of D22 catch a regression.
- **Selects use the customizable select** (`appearance: base-select`, `::picker(select)`), which styles the picker and its options with the console's tokens and keeps the native element (keyboard, form value, screen reader). A browser without it shows the native picker (progressive enhancement); `color-scheme` on the control keeps that picker readable in dark mode. A story opens the picker and checks its contrast in both themes. Per M3 ("Use radio buttons when there are five or fewer options"), a choice of five or fewer in an editor is a radio group: the concert type (単独公演, ツアー, フェス) becomes radios; the sale's verification requirement and the time fields stay selects.
- **Rejected — `@material/web`:** in maintenance mode, no time picker, and `refactor-shared-ui-design-system` Decision 1 already declined it (kept in D12).

### D17 — Text is translated in templates, never in view-models

- A view-model exposes catalog keys and their parameters (`{ key, params }`, as `FieldError` already does), and the template translates with `t="…"` or `& t` (the `@aurelia/i18n` standard). A language switch then re-renders every text. Option lists, table column titles and business detail labels are keys too.
- The snackbar (`ISnackbar`) and the confirmation dialog take keys and parameters and translate in their own templates, so a text shown while the language changes follows it. Formatted values (dates, yen, counts) stay value converters with the `& signal` of the language (`organizer/i18n/converters.ts`).
- A unit test fails on any `tr(` call in `frontend/organizer/**` outside `organizer/i18n/`, next to the existing literal-text check (`test/organizer/i18n/catalog.spec.ts`).

### D18 — Screens follow M3 components and canonical layouts

Each screen was redesigned against the M3 guideline pages, rendered and read on 2026-10-13 (m3.material.io `components/<name>/guidelines` and `foundations/layout/canonical-examples/*`; the quotes below are verbatim). The rules applied everywhere:

- **One filled button per screen**, for the action that completes its flow (保存する, 公開する); secondary actions are outlined or tonal; dialogs use text buttons (M3 Buttons). Destructive actions that are not the screen's purpose (公演を中止, 中止する) sit in an overflow menu in the page header (M3 Menus: "a menu takes up less space"; disabled rather than removed when unavailable).
- **Collections are lists, not cards, on compact windows**: a list item is one action that opens its detail ("Lists should extend edge-to-edge in compact windows. Selecting a list item should open a page with the details."); trailing text carries the date or state. From 840 px (M3 expanded) a collection that is compared across rows is a table whose whole row opens the item (one link per row, stretched over the row). Cards remain only where a group holds several different actions (a sale on the Sales tab).
- **Dialogs only for confirmations and discarding changes**, a title that names the action and object (never "Are you sure?"), at most two actions, the confirming one naming the action (M3 Dialogs). The dismissive label is やめる / Cancel (the English "Keep as is" goes).
- **Loading** shows one linear progress indicator at the top of the page; a pending action shows a circular indicator inside its button (M3 Progress indicators). **Snackbars carry no icons** (M3 Snackbar: "Avoid adding icons") and, because auto-dismissing snackbars are not accessible on web, every result is also visible on the page it lands on (the new state, or the page the save returned to).
- **Fields** are outlined text fields with a visible label, an asterisk on required fields explained once per form, and the error replacing the supporting text with an error icon (M3 Text fields).

Per screen:

| Screen | Layout and components |
|---|---|
| Shell | Navigation bar below 600 px, rail from 600 px (M3: bar for compact, rail for medium and wider, never both). Top app bar: on compact a back arrow to the parent, then the page title; the Artist menu button (D1) and the account menu (language, サインアウト) at the trailing edge. On medium and wider, the brand lockup (D20) heads the rail and the breadcrumb sits above the page title. |
| Home | A single-action list grouped by kind with subheaders (要対応, 7日以内, 開始時刻なし, 下書き); each item opens where it is resolved; its date as trailing text. No buttons in items. |
| Concerts (of an Artist) | Compact: a three-line list (title; first date · venue and 他 N公演; sale state) with the publish state as a labelled status at the trailing edge. Expanded: a table with the columns of spec `route/concerts`. 公演をつくる is an extended FAB (M3: "the most important action on a screen"), at the bottom trailing corner above the navigation bar on compact and at the bottom trailing corner on wider windows. |
| Concert | Supporting-pane layout (M3 canonical): the focus pane lists the dates as single-action items opening each event; the supporting pane holds the summary (cover, type, visibility, performers), beside the focus pane from 840 px and below it on narrower windows. Header actions: 公開する (filled, while a draft date exists), 編集 (outlined), overflow menu with 公演を中止. |
| Event | Header: date and time JST, venue, publish status, the fan page link of a published date of a PUBLIC concert (D21). Actions: 公開する (filled, draft only), overflow menu with 中止する and 公演を編集. Primary tabs 販売 and 受付 under the header (M3 Tabs, at most four). |
| Sales tab | One card per sale (it holds several different actions): name, method, window JST, state; stat tiles; 編集 (text button) and the verification requirement select. 抽選で販売する and 先着で販売する are outlined buttons above the cards; prerequisites are callouts with their fix link. |
| Reception tab | A multi-action list: each scanner's name, state and URL as content; copy as a trailing icon button and the overflow menu (取り消す, 取り消して再発行). 受付リンクを発行 is a tonal button. |
| Concert editor, sale editors | Full pages (M3 reserves full-screen dialogs for compact windows), one column of outlined fields capped at 600 px, sections separated by headings and spacing, not dividers. The action bar at the bottom holds キャンセル (text) and 保存する (filled). |
| Settings | Sections with headings: 組織, アーティスト, 事業者情報 (description lists, read only), 入金口座 (status, the explanation before the hand-off, then the outlined button `Stripe で登録を続ける` with an external-link icon). |

### D19 — Event dates and times in the editor

- **24-hour time entry.** A console time field of two selects, hour 00-23 and minute 00-55 in 5-minute steps, labelled JST, with no AM/PM (M3 Time pickers: "Hours and minutes should have separate inputs… For people using a 24-hour clock, the AM/PM selector shouldn't appear"). Selects accept typed digits from the keyboard, which covers M3's "manual time entry". Estimated 100-150 lines with its story; no dial. The same field replaces every `datetime-local` and `time` input of the console (the concert editor, the lottery and first-come sale windows): a date field plus this time field. Dates stay `<input type="date">` (the owner reported no problem with dates).
- **Defaults.** The first date row of a new concert starts with 開場 17:00 and 開演 19:00 (owner, 2026-10-13). 日程を追加 copies the previous row's venue (with its picked place), date, open and start time, so a run of nights at one venue needs only the date changed.
- **Save returns.** A successful save returns to the page the editor was opened from (the concert page; for a new concert, the new concert's page) and confirms in the snackbar, replacing "keeps the editor open". The landing page shows the saved values, which also gives the inline confirmation M3 asks for on web.

### D20 — Names

- The console names itself only with names the project defined: the brand "Liverty Music" and the product name "Organizer Console", in English in both languages (owner, 2026-10-13). "Liverty Organizer" and the short form "Liverty" are not used. The page title is `<page> — Organizer Console`.

### D21 — Fan page link instead of the share link, for now

- A published date of a PUBLIC concert shows its fan page address (`https://<fan origin>/events/<event id>`, the page of story `open-a-shared-event-link`) with a copy action on the event page. The fan origin comes from the existing environment map (`frontend/shared/config/known-hosts.ts` `KNOWN_HOSTS`), so no new config key is needed.
- The UNLISTED share link is removed from the console until fans can open one: no fan route reads the token, and `/events/<id>` of an UNLISTED concert answers not found (fan `route/event` "Event without a page"). A follow-up change gives UNLISTED concerts a fan entry (backend returning a full URL, a fan route reading the token) and brings 新しい共有リンクを発行 back. The referral link (`?ref=`) is a separate change too (owner, 2026-10-13).
- The editor keeps 限定公開: an UNLISTED concert notifies no follower when published, which the owner's walk-through relies on (task 7.2).

### D22 — Rendered checks

- Functional tests run axe on every console screen in light and dark at 390 × 844 and 1280 × 800, failing on any violation (including `color-contrast`), with `@axe-core/playwright` as a new dev dependency (the storybook projects already run axe per component; a screen check catches what composition breaks, such as D16's leak).
- Before a screen is called done, it is looked at rendered in both themes and widths, and the story is walked end to end, including external hand-offs (`feedback`: the walk-through found what the suites passed).

## Risks / Trade-offs

- [One sale read per published event on lists (D2)] → Acceptable at tens of events; add a sale summary to the `SeriesService` List response if Concerts takes over 1 s to show sale states.
- [The console checks business details before a lottery, the server does not (`usecase/ticket-sale/create` has no such precondition)] → The console gate is a UX gate only; the server-side precondition is liverty-music/specification#1135; see "Assumptions to confirm" 3.
- [Fan visual change from 12 % to 10 % state layers] → Small and intended (M3 values); the fan functional test `e2e/functional/press-state.spec.ts` asserts only that a layer appears (opacity above 0), so it passes unchanged.
- [View Transitions not in every browser] → Progressive enhancement; navigation works without it.
- [Shadow DOM components in a light-DOM codebase (D16)] → Confined to `frontend/organizer/ui`; pages stay light DOM. Native controls stay inside the component that labels them, so forms and labels keep working.
- [A concert has one address per represented performer (D1)] → Harmless in a private console; the breadcrumb follows the address.
- [Large frontend rewrite of one app] → The console has no users; screens land in one PR per group behind no flag, and each group's tests gate it.
- [Three predecessors must land first] → Group 0 blocks the work; the shared-code group (3) and the venue search (1-2) do not depend on them and can start at once.

## Migration Plan

1. Proto PR (Venue `place_id`, `VenueService.Search`, `EventDraft.place_id` required), Release, BSR gen.
2. Backend PR (venue search, venue on the authored read, place required in draft creation), deploy; the first console search is checked in the logs after step 4 (task 6.10).
3. Frontend PR: shared tokens, snack bar move, circular progress (fan app). Can ship before the console.
4. Frontend PRs: console foundation and shell, then screens. Old routes and components are deleted in the same PRs that replace them.
5. Production: the owner's walk-through (task 7.2); read-only checks of the rollout.
6. Rollback: revert the frontend PR. `Venue.place_id` and `VenueService.Search` are additive and can stay. The required `EventDraft.place_id` is not: between steps 2 and 4 the current editor saves only when its raw place id field is filled, and reverting the console after step 4 needs the backend requirement reverted too.

## Assumptions to confirm

1. **Venue search runs through a new backend call** (`VenueService.Search`), as the operator types since 2026-10-13 (D9), with Japanese names and places in Japan ranked first (D9), rather than browser-side Maps autocomplete. The plan had filed the place id bug as a separate issue; the brief puts the fix here, which adds a proto and backend part to this change.
2. **The Venue read exposes its place id** so that an unchanged row is resent with it; without this the editor cannot keep the venue match.
3. **Missing business details block both methods in the console.** The business details disclosure (特商法 表記) applies to any paid sale. Since `unify-ticket-sales` and `first-come-ticket-sales` archived, `usecase/ticket-sale/create` checks them for neither method, so the console gate is a UX gate only; the server-side precondition is liverty-music/specification#1135 (not in this change).
4. **Publish and cancel act per event, and the concert page acts on its dates together** (D14, owner decision 2026-10-13, replacing the earlier "no cancel on the concert page").
5. **"Draft concerts" on Home means a concert with at least one draft event.**
6. **Drawn lottery tiles show tickets won**, not tickets issued: the entry stats (`lottery-entry/get-stats-by-ticket-type`) return Won tickets; issuance follows within 1 minute (`unify-ticket-sales` D5), so the numbers match once issuance runs.
7. **The share link is only shown when created.** The Series' token is never returned on reads, so the concert page cannot show the current link; it offers a new link with a confirmation that the old one stops working. Superseded on 2026-10-13 by D21: the share link leaves the console until fans can open it.
8. **The reception guide link appears only once the guide exists.** (先着で販売する is offered from the start: `first-come-ticket-sales` archived on 2026-10-11.)
9. **Old addresses are not redirected**; unknown addresses open Home.
10. **The fan app's focus and pressed state layers change to 10 %**, because the system tokens are shared; the plan said the fan app changes only its easing token.

## Open Questions

- Exact light and dark values of each console color role: tuned during implementation against the contrast test; does not change specs or tasks.
