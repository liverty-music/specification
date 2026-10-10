## Context

See proposal.md - Why. The UX plan agreed with the owner (claims, mocks and sketches, 2026-10-10) is the source of the screens; the decisions below override it where they differ.

Current state, verified in the code on 2026-10-10 (frontend `main` at `e0f6c3d`):

- **Shell and routes.** `frontend/organizer/organizer-shell/organizer-shell.ts:23-87` is one flat route list (`concerts`, `concerts/new`, `concerts/edit/:seriesId`, `lottery/configure/:eventId`, `lottery/status/:phaseId`, `reception-links/:eventId`, `welcome`, `denied`, `auth/callback`); the comment at `:46-51` admits the lottery editor is reachable only by deep link. `organizer-shell.html` is a bare `<au-viewport>`. No organizer file calls `IAuthService.signOut` (`shared/services/auth-service.ts:348`), so there is no sign-out.
- **Publish without confirmation.** `concerts/concerts-route.ts:209-224` publishes on one click; the class comment at `:156-157` says Publish and Cancel are confirmed, but only Cancel has a two-step reveal (`concerts-route.html:79-133`).
- **Venue field.** The editor asks for a raw place id (`concert-editor/concert-editor-route.html:134-139`, placeholder `ChIJ…`), and `concert-editor-route.ts:230` hydrates every event with `placeId: ''`, so each save resends the venue by name only. The read side cannot do better today: `entity/v1/venue.proto:9-21` has no place id although the Venue entity has one (`specs/components/entity/venue`), while `EventDraft.place_id` exists on write (`rpc/organizer/series/v1/series_service.proto`, `EventDraft`).
- **Save feedback.** `concert-editor-route.ts:283-315` sets `saveError` on failure and shows nothing on success.
- **Time zone.** `concert-editor/concert-form.ts:92-105` builds event times in the browser's time zone; `lottery-phase-editor/lottery-phase-form.ts:60-80` does the same for the window; `lottery-status/lottery-status-route.ts:35` uses `toLocaleString()`. A Japan-time formatter already exists for the reception screens (`shared/lib/reception/jst-format.ts`).
- **No i18n.** `organizer/main.ts:147-162` registers "NO i18n machinery"; every string is English. The fan app's set-up is `src/main.ts:166-190` (`I18nConfiguration`, `fallbackLng: 'ja'`, detection querystring → localStorage → navigator).
- **Styles.** `organizer/styles/main.css` (245 lines) copies a subset of the fan tokens with the fan app's dark navy surface. The fan tokens have `--md-easing-emphasized-accelerate: cubic-bezier(0.3, 0.8, 0.15, 1)` at `src/styles/tokens.css:146` (wrong), state layers focus and pressed 12 % at `:251-252`, and only `long2`/`long4` of the long durations.
- **Fan primitives.** `<loading-spinner>` is registered at `src/main.ts:291` and used only at `src/routes/verify-callback/verify-callback-route.html:6`. `<snack-bar>` lives in `src/components/snack-bar/` (default 2500 ms, `snack.ts:29`; `Infinity` supported, `snack-bar.ts:62-68`) and is mounted in `src/app-shell.html:28`.
- **Backend reads the console can use.** `OrganizerService.Get` / `ListArtists`, `PayoutOnboardingService.Get` (account status plus `onboarding_url` while not active), `ConcertService.List` (authored concerts with events and their ids) and `RegenerateToken` (returns the new share token; the Series' token is "never shown on reads", `specs/components/entity/series`). After `unify-ticket-sales`: `TicketSaleService.List(event_id)` with tallies per TicketType (`usecase/ticket-sale/list-own-by-event`: entries, requested tickets, Won entries, Won tickets, Lost entries) and `SetVerificationRequirement`.
- **Map catalog.** The backend already calls Places Text Search with Application Default Credentials (`backend/internal/infrastructure/maps/google/client.go:27,90`, `SearchPlace` returns one best match). No browser Maps key exists.
- **M3 values**, fetched today from AndroidX sources: `StateTokens.kt` hover 0.08, focus 0.10, pressed 0.10, dragged 0.16 (no selected value); `MotionTokens.kt` durations 50-1000 ms and easings standard (0.2,0,0,1), standard-accelerate (0.3,0,1,1), standard-decelerate (0,0,0,1), emphasized-accelerate (0.3,0,0.8,0.15), emphasized-decelerate (0.05,0.7,0.1,1); `SnackbarHost.kt` Short 4000 ms, Long 10000 ms, Indefinite. Window size classes (compact < 600, medium 600-839, expanded 840-1199 dp) and the 48 dp target come from the brief's check of the Android Developers docs; not re-fetched here.

Constraints: bundle isolation (`make verify-bundle-isolation`, `lint-boundaries`: only `shared/` crosses between `src/`, `admin/`, `organizer/`, `reception/`); CUBE CSS with the repository's stylelint plugin; no users, dev stopped.

## Goals / Non-Goals

**Goals:**
- One console structure that the three preceding changes plug into, usable at 360 px and at 1920 px.
- Share code with the fan app only where both apps need the same behavior.

**Non-Goals:**
- The admin console shell (from `refactor-shared-ui-design-system`); follow-up issue (task 0.6).
- The first-come sale editor and its states (`first-come-ticket-sales`); this change gives it the Sales tab entry.
- The reception screen staff use at the door and the reception guide (`ticket-wallet-and-checkin`, `isolate-venue-reception`).
- Editing a sale after creation, refunds, settlement statements, a pre-publish preview, a sales checklist (story-map items without an RPC; listed in the plan).
- Changing the fan app's colors, type or components beyond the shared tokens, the snack bar move and the spinner replacement.
- A `ConcertService.Get`: `List` is enough for an Organizer's small catalog (the plan's decision).

## Decisions

### D1 — Routes: every screen has one parent

| Address | Screen | Parent (breadcrumb) | Destination |
|---|---|---|---|
| `home` (also `''` and any unknown address) | Home | — | ホーム |
| `concerts` | Concerts | — | 公演 |
| `concerts/new` | Concert editor (new) | Concerts | 公演 |
| `concerts/:seriesId` | Concert | Concerts | 公演 |
| `concerts/:seriesId/edit` | Concert editor | Concert | 公演 |
| `concerts/:seriesId/events/:eventId/sales` (default tab) | Event, Sales tab | Concert | 公演 |
| `concerts/:seriesId/events/:eventId/reception` | Event, Reception tab | Concert | 公演 |
| `concerts/:seriesId/events/:eventId/sales/new-lottery` | Lottery sale editor | Event | 公演 |
| `concerts/:seriesId/events/:eventId/sales/new-first-come` | First-come sale editor (`first-come-ticket-sales`) | Event | 公演 |
| `settings` | Settings | — | 設定 |
| `denied`, `auth/callback` | unchanged | — | — |

- Removed: `lottery/configure/:eventId`, `lottery/status/:phaseId`, `reception-links/:eventId`, `welcome`, `concerts/edit/:seriesId`. No redirects: there are no users, and the fallback opens Home.
- **Why the event id stays under the concert:** the breadcrumb needs the concert, and `ConcertService.List` is the only read; a flat `events/:eventId` would need a reverse lookup across all concerts.
- Tabs are child routes so a tab is a shareable address (spec "Reception tab address"). The tab bar is an M3 primary tabs component driving the router.
- Each route declares its parent in route `data`; one breadcrumb component in the shell renders it (compact: the parent only).

### D2 — Data per screen, no new read RPC

| Screen | Reads |
|---|---|
| Home | `ConcertService.List`, `PayoutOnboardingService.Get`, and for each published event starting within 7 days the scanner list of `rename-reception-to-scanner` (an Organizer has a handful of such events; calls run in parallel) |
| Concerts, Concert | `ConcertService.List`; sale state per event from `TicketSaleService.List` for published events only, lazily per visible event |
| Event | `ConcertService.List` (find the event), `TicketSaleService.List(event_id)`, `OrganizerService.Get` (business details prerequisite), scanner list |
| Settings | `OrganizerService.Get`, `OrganizerService.ListArtists`, `PayoutOnboardingService.Get` (re-read on `visibilitychange` to visible) |

- **Sale state on lists** costs one `TicketSaleService.List` per published event. With the current catalog (tens of events) this is acceptable; the plan's alternative (a sale summary on the `SeriesService` List response) is the follow-up if lists get slow. Recorded, not built.
- Countdown and "open/closed" are computed on the client from the sale's times and the clock, refreshed every 60 s; the server stays the source of truth for whether an entry is accepted.

### D3 — Responsive layout: window class for navigation, container class for lists

- Navigation: one CSS media query at `width >= 600px` switches the M3 navigation bar (bottom, 80 px high, 3 items) to the M3 navigation rail (80 px wide). Expanded windows (≥ 840 px) keep the rail rather than a navigation drawer: three destinations do not need a drawer (M3 recommends a drawer for 5+ destinations or expanded labels).
- Lists: the card list component sets `container-type: inline-size`; `@container (width >= 840px)` renders a `<table>` with the same data. Both are rendered from one template branch per mode, not by restyling a table into cards, so screen readers get real table semantics on wide screens and a list on narrow ones.
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

- Console tokens live in `frontend/organizer/styles/tokens.css` with the fan role names (`--md-sys-color-surface`, `on-surface`, `primary`, …) and values from `light-dark()`, with `color-scheme: light dark` on `:root`. Brand magenta `oklch(65% 0.28 350deg)` stays the `primary` role; status colors (success, warning, error, neutral) are separate roles, always beside a text label.
- Type scale fixed in px from M3 `TypeScaleTokens.kt` (body-large 16/24, body-medium 14/20 default, label-large 14/20, title-medium 16/24, title-large 22/28, headline-small 24/32); font stack `"Hiragino Sans", "Noto Sans JP", "Yu Gothic UI", system-ui, sans-serif`; `font-variant-numeric: tabular-nums` on numbers.
- **This amends Decision 2 of `refactor-shared-ui-design-system`** (fluid `clamp()` scales everywhere) for the console: an operator compares numbers across windows, and M3 adapts layout, not text size, across window classes.
- Contrast is checked in tests by computing role pairs (D10).

### D7 — Language, time and money

- `@aurelia/i18n` registered in `organizer/main.ts` like `src/main.ts:166-190`, with `detection.order: ['localStorage', 'navigator']`, `fallbackLng: 'ja'`, `supportedLngs: ['ja','en']`, and the same `lng: undefined` override. Catalogs in `frontend/organizer/locales/{ja,en}/translation.json`. Operators have no User row, so the choice is per device only (the console origin has its own localStorage). A locale-changed subscriber sets `document.documentElement.lang`.
- Dates: `Intl.DateTimeFormat(locale, { timeZone: 'Asia/Tokyo', … })` followed by "JST". Entry: `<input type="datetime-local">` / `date` / `time` values are read as wall-clock parts and converted with a fixed +09:00 offset (Japan has no daylight saving time), replacing `new Date(y, m, d, h, min)` in `concert-form.ts` and `lottery-phase-form.ts`. The reception helper `shared/lib/reception/jst-format.ts` stays for the reception app.
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

- New `ConcertService.SearchVenues(text) → repeated VenueCandidate {place_id, name, address}` on the organizer concert service; `ConcertAuthoringUseCase.SearchPlaces` validates the text and calls `Venue.SearchPlaces`, implemented on the existing Google client with `places:searchText`, `pageSize: 5`, `languageCode: ja`, `regionCode: JP`, field mask `places.id,places.displayName,places.formattedAddress`.
- The field searches on an explicit action (search button or Enter), not on every keystroke: operators enter a few venues a month, and this keeps calls to one per search with no debounce state.
- `Venue` gains an optional `place_id` on reads and the authored-concert mapper fills it, so the editor resends the place of an unchanged row (spec "An unchanged venue is kept on save"). Today the mapper sets no venue at all on authored events (`backend/internal/adapter/rpc/mapper/organizer_concert.go:117` `AuthoredEventsToProto`), which is why every reload empties the field; the mapper now sets `Event.venue` (id, name, place id) from the authored read.
- **A picked place is required (owner decision, 2026-10-10).** `EventDraft.place_id` becomes required in the proto, and `usecase/series/create-draft` rejects an event without one. A typed name alone used to create a Venue keyed by name with no admin area (`seriesDraftToInputs` never sets one), so same-named halls in different cities merged into one Venue, and new Venues had no coordinates, so location-based fan lists missed them.
- **New Venue from the catalog's place.** When no Venue holds the picked place id, `Venue.GetPlace` reads the place with Places Details (`GET places/{id}`, field mask `id,displayName,location,addressComponents`, `languageCode: ja`); the admin area is the ISO 3166-2 code of the `administrative_area_level_1` component (the existing prefecture-name mapping in `internal/infrastructure/geo` covers JP). One Details call per new venue; the search already paid for the pick.
- **Rejected — keep the typed name when nothing matches:** it is the path that produced merged and location-less Venues. A venue the catalog does not know is not expected for the pilot; if one appears, the fix is to add it to the map catalog, not to accept free text.
- **Rejected — Maps JavaScript Places Autocomplete in the browser:** a new browser API key to provision and restrict, a third-party script and CSP entries in the console, for an action the backend can already serve with its existing credentials.
- **Cost (inferred, not checked against billing):** Text Search with name and address is a Pro-tier SKU; at a few dozen searches a month it is far below the monthly free usage.

### D9a — Cover preview until the processed image replaces it

- Today the editor clears `coverImageUrl` after AttachMedia and never reads again (`frontend/organizer/concert-editor/concert-editor-route.ts:347-350`), so the processing note stays until a reload. The backend keeps the previous media on the Series until the processor cuts over (`MediaUseCase.ProcessMedia` → `CutOverSeriesMedia`), so a save before processing re-hydrates the editor with the previous cover's URL.
- After AttachMedia the editor re-reads the concert (the existing `ConcertService.List` read) every 3 s for up to 60 s and swaps to the processed image once the Series' media id equals the uploaded one. While the returned media id differs, `hydrate` keeps the local preview. After 60 s the note says processing is taking longer and the next open shows the result.
- **Rejected — a media status RPC:** one more read surface for a few uploads a month; the authored read already carries the media id.

### D10 — Testing approach

- Components and screens: Vitest + `@aurelia/testing` per scenario, with the Connect clients mocked.
- Layout and motion: Playwright functional tests (`e2e/functional`, existing `page.route` mocking and `support/auth-mocks.ts`) at 390 × 844 and 1280 × 800, including `prefers-reduced-motion` and `prefers-color-scheme` emulation.
- Contrast: a unit test computes the contrast of every role pair in both themes from the token file.
- Story: a Playwright functional test with mocked RPCs for both widths, plus one production walk-through by the owner (passkey sign-in cannot be automated) on an UNLISTED test concert whose performer has no followers, so publishing notifies no one.

### D11 — Spec handling of in-flight changes

- `route/reception-links` (added by `ticket-wallet-and-checkin`, not yet in the main specs) is written as a REMOVED delta here; `openspec validate --strict` accepts it now, and it applies once `ticket-wallet-and-checkin` archives. If `rename-reception-to-scanner` moves that spec, task 0.3 retargets the delta.
- `route/lottery-phase-editor` keeps its path in this change. Once `unify-ticket-sales` and `first-come-ticket-sales` are both archived, the lottery editor and the first-come `route/ticket-sale-editor` are one screen family; merging the two main specs into `route/ticket-sale-editor` is a main-spec move done directly with a mapping table (task 8.1), not a delta.
- Publish and cancel are written as acting on an event. The exact usecase names come from `restructure-event-publishing`; task 0.2 aligns the story and the event page wording once it is archived.

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

## Risks / Trade-offs

- [One sale read per published event on lists (D2)] → Acceptable at tens of events; add a sale summary to the `SeriesService` List response if Concerts takes over 1 s to show sale states.
- [The console checks business details before a lottery, the server does not (`usecase/ticket-sale/create` has no such precondition)] → The console gate is a UX gate only; see "Assumptions to confirm" 3.
- [Fan visual change from 12 % to 10 % state layers] → Small and intended (M3 values); the fan functional test `press-state.spec.ts` is updated in task 3.1.
- [View Transitions not in every browser] → Progressive enhancement; navigation works without it.
- [Large frontend rewrite of one app] → The console has no users; screens land in one PR per group behind no flag, and each group's tests gate it.
- [Three predecessors must land first] → Group 0 blocks the work; the shared-code group (3) and the venue search (1-2) do not depend on them and can start at once.

## Migration Plan

1. Proto PR (Venue `place_id`, `SearchVenues`), Release, BSR gen.
2. Backend PR (venue search, mapper), deploy; verify `SearchVenues` with a read-only call from the console after step 4.
3. Frontend PR: shared tokens, snack bar move, circular progress (fan app). Can ship before the console.
4. Frontend PRs: console foundation and shell, then screens. Old routes and components are deleted in the same PRs that replace them.
5. Production: the owner's walk-through (task 7.2); read-only checks of the rollout.
6. Rollback: revert the frontend PR; the proto and backend additions are additive and can stay.

## Assumptions to confirm

1. **Venue search runs through a new backend call** (`ConcertService.SearchVenues`) on an explicit search action, with Japanese names and places in Japan ranked first (D9), rather than browser-side Maps autocomplete. The plan had filed the place id bug as a separate issue; the brief puts the fix here, which adds a proto and backend part to this change.
2. **The Venue read exposes its place id** so that an unchanged row is resent with it; without this the editor cannot keep the venue match.
3. **Missing business details block both methods in the console.** `first-come-ticket-sales` requires them for first-come; `unify-ticket-sales` does not check them for a lottery. The seller disclosure (特商法 表記) applies to any paid sale, so the console shows the prerequisite for both. Recommended: add the same precondition to `TicketSaleUseCase.Create` for Lottery (not in this change).
4. **Publish and cancel act per event** (after `restructure-event-publishing`). Whether a concert-wide cancel remains is that change's decision; the concert page in this change has no cancel action.
5. **"Draft concerts" on Home means a concert with at least one draft event.**
6. **Drawn lottery tiles show tickets won**, not tickets issued: the tallies (`get-ticket-type-stats`) return Won tickets; issuance follows within 1 minute (`unify-ticket-sales` D5), so the numbers match once issuance runs.
7. **The share link is only shown when created.** The Series' token is never returned on reads, so the concert page cannot show the current link; it offers a new link with a confirmation that the old one stops working.
8. **先着で販売する appears only once `first-come-ticket-sales` ships**; until then the Sales tab offers the lottery only. Likewise the reception guide link appears only once the guide exists.
9. **Old addresses are not redirected**; unknown addresses open Home.
10. **The fan app's focus and pressed state layers change to 10 %**, because the system tokens are shared; the plan said the fan app changes only its easing token.

## Open Questions

- Exact light and dark values of each console color role: tuned during implementation against the contrast test; does not change specs or tasks.
