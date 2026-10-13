## Why

The organizer console is where an Organizer's operators create concerts, put events on sale and prepare the door, but today it is a set of English-only screens behind a bare viewport: there is no navigation, no sign-out, no way back from the lottery and reception screens, and two screens are reachable only by typing their address. Publishing an event, which notifies every follower of its performers, fires on one click. Dates are read in the browser's time zone, and nothing says whether a save succeeded. Operators work on a PC in the office and on a phone at the venue, so the console must work on both. Three changes now reshape what the console shows (`unify-ticket-sales`, `restructure-event-publishing`, `rename-reception-to-scanner`), so this is the moment to rebuild its structure once, following Material Design 3 (M3) guidance, instead of patching each screen as those changes land.

## What Changes

- **New information architecture.** Home (what needs the operator now), Concerts, a page per concert, the concert editor, a page per event (one per event date) with a Sales tab and a Reception (受付) tab, and Settings. Every screen has a parent and a breadcrumb; no screen is reachable only by its address.
- **BREAKING (console routes)**: the addresses `lottery/configure/:eventId`, `lottery/status/:phaseId`, `scanners/:eventId`, `welcome` and `concerts/edit/:seriesId` go away. Their content moves into the event page tabs, the concert page and Home. The product has no users, so no redirect is kept; an unknown address opens Home.
- **Sales tab** lists an event's TicketSales with their TicketTypes and shows each lottery as scheduled (with a countdown), open (entries, requested tickets, quantity) or drawn (winners, tickets won, losers), and each first-come sale by its state with sold and held counts. It explains a missing prerequisite with a link to fix it, starts a lottery or a first-come sale, edits a first-come sale at any time and a lottery before it opens, and changes a sale's verification requirement.
- **Publishing and cancelling** (owner decision, 2026-10-13): the concert page publishes the draft dates the operator chooses in one action, so followers are notified once, and cancels the whole concert; the event page publishes or cancels its own date. The concerts list has no actions: `restructure-event-publishing`'s Publish on the list is removed. The concert editor gains the visibility choice (公開 / 限定公開), which it never had.
- **Reception tab** takes over the scanners screen (`route/scanners`, the Scanner vocabulary since `rename-reception-to-scanner`; UI copy 受付 stays).
- **Settings** shows the Organizer, its represented Artists and its business details (read only, entered by Liverty Music during vetting) and the payout account status with the link to finish onboarding.
- **Responsive layout per the M3 window size classes**: a navigation bar below 600 px, a navigation rail from 600 px; lists are cards and become a table when the list area is at least 840 px wide; every control has a target of at least 48 × 48 px.
- **Feedback per M3**: state layers, a confirmation dialog naming the effect before publishing, cancelling, regenerating a share link or revoking a scanner; a progress indicator inside a pending button; one snackbar host (4 s, an error with Retry stays until dismissed); form errors next to the field; an unsaved-changes guard on the editors; short motions that collapse under reduced motion.
- **Style**: light by default and dark when the OS is dark, using the shared token role names with the console's own values; the fixed M3 type scale with Japanese system fonts and tabular numerals.
- **Language and time**: Japanese and English; every date and time shown and entered in Japan time with "JST"; prices with separators in yen.
- **Venue search**: the concert editor finds a venue by searching the map catalog instead of asking for a raw place id, and keeps the venue of an unchanged event row on save (today every save drops it). **BREAKING (authoring)**: every event's venue is a place picked from the map catalog. A typed name alone is no longer saved, so two same-named halls in different cities (CLUB QUATTRO in Shibuya and Umeda) stop merging into one Venue, and a new Venue is created with the place's coordinates and admin area, so it appears in location-based fan lists. A published or cancelled date keeps its Venue on Update, which does not read the venue given for it, so dates published before this change can still be corrected.
- **Cover image preview**: the editor swaps the picked image for the processed one while it is open, and a save before processing finishes no longer brings back the previous cover.
- **Shared with the fan app (only where both need the same behavior)**: the M3 system tokens (state layers, motion durations, easing) in one source, which fixes the fan app's wrong emphasized-accelerate curve and aligns its focus and pressed state layers to 10 %; the snack bar component; an M3 circular progress indicator that replaces the fan `<loading-spinner>`, which is removed.
- **Absorbs** the still-valid parts of `refactor-shared-ui-design-system` (console navigation with no dead-end screens; shared tokens and primitives, narrowed to what both apps need). Its admin console shell is not part of this change. design.md lists which of its requirements this change supersedes.

## Capabilities

### New Capabilities

- `components/infrastructure/organizer/web/global/design-tokens`: the console's color roles with light and dark values, type scale, fonts, shape, state layers and motion
- `components/infrastructure/organizer/web/global/i18n`: Japanese and English, language detection and switching, Japan time and yen formatting
- `components/infrastructure/organizer/web/global/snack-bar`: the console's single snackbar host and its durations
- `components/infrastructure/organizer/web/global/action-feedback`: how every console control reacts: target size, state layers, pending buttons, confirmation dialogs, form errors, unsaved-changes guard, copy and small motions
- `components/infrastructure/organizer/web/route/home`: the list of what needs the operator now
- `components/infrastructure/organizer/web/route/concert`: one concert's summary, performers, share link, publishing and cancelling its dates together, and its event dates
- `components/infrastructure/organizer/web/route/event`: one event's page with its Sales and Reception tabs
- `components/infrastructure/organizer/web/route/settings`: the Organizer, represented Artists, business details and payout account
- `components/entity/venue/search-places`: looks up candidate places for a venue name in the map catalog
- `components/usecase/venue/search`: an operator searches the map catalog for a venue while authoring a concert
- `components/entity/venue/get-place`: reads the picked place's name, coordinates and admin area from the map catalog
- `stories/run-an-event-from-the-organizer-console`: publish an event, open a sale, issue scanners, all reached by navigation

### Modified Capabilities

- `components/infrastructure/organizer/web/global/organizer-shell`: the route guard lands on Home; persistent navigation, breadcrumbs, sign-out and the responsive layout
- `components/infrastructure/organizer/web/route/concerts`: the list of concerts with responsive cards and table; the per-row lottery entry point moves to the event page; Publish and Cancel on the list (added by `restructure-event-publishing`) are removed, moving to the concert and event pages
- `components/infrastructure/organizer/web/route/concert-editor`: venue search with a required pick, Japan time entry, save feedback, the unsaved-changes guard, and the cover preview kept until the processed image replaces it; the visibility choice
- `components/usecase/series/update`: a new or DRAFT event needs a picked place id; the venue given for a PUBLISHED or CANCELLED Event is not read (modifies requirements `restructure-event-publishing` adds; task 0.2)
- `components/usecase/series/create`: "Each event's venue is found or created" is replaced by "Each event's venue is a picked place": every event gives a picked place id; a new Venue is created from the catalog's place with coordinates and admin area, never from a typed name (`restructure-event-publishing` modifies another requirement of this spec, "Draft stored as DRAFT")
- `components/infrastructure/organizer/web/route/lottery-sale-editor`: opened from the event's Sales tab and returns there; window entered in Japan time; changes a lottery sale's window, price, quantity and per-account limit before it opens
- `components/infrastructure/organizer/web/route/scanners`: removed; its requirements move to the event page's Reception tab. The spec came from `ticket-wallet-and-checkin` as `route/reception-links` and was renamed by `rename-reception-to-scanner` (both archived; tasks 0.3, 0.4)
- `components/adapter/organizer/api/rpc/series`: the venue search call passes the same sign-in checks as the other authoring calls
- `components/infrastructure/fan/web/global/design-tokens`: state layers at the M3 values, M3 easing values, and the system tokens shared with the console
- `components/infrastructure/fan/web/global/ui-primitives`: the loading spinner is replaced by an M3 circular progress indicator

Entity operations this change relies on and does not change: `Series.GetAuthored`, `Series.SetUnlistedToken` (through `SeriesUseCase.RegenerateShareUrl`), `Venue.GetByPlaceId`, `Organizer.Get` and `Organizer.ListArtists` (through `OrganizerUseCase.Get` and `ListOwnArtists`), the PayoutAccount read, `TicketSale.ListByEvent` and `LotteryEntry.GetStatsByTicketType` (through `TicketSaleUseCase.ListOwnByEvent`), `TicketSale.SetWindow` and `TicketType.Update` (through `TicketSaleUseCase.SetWindow` and `TicketTypeUseCase.Update`), and the scanner list, issue and revoke operations of `ticket-wallet-and-checkin` as renamed by `rename-reception-to-scanner`.

## Impact

- **frontend**: `frontend/organizer/**` rebuilt (shell, routes, `organizer/ui` components, i18n catalogs); `frontend/shared/styles/m3-sys.css` (new), `frontend/shared/ui/snack-bar` (moved from `frontend/src/components/snack-bar`), `frontend/shared/ui/progress-indicator` (new); `frontend/src/styles/tokens.css` (state and easing values now from the shared file); `frontend/src/components/loading-spinner` removed and its one use in `frontend/src/routes/verify-callback` replaced. `@aurelia/i18n` is added to the organizer entry. Bundle isolation (`scripts/verify-bundle-isolation`) must stay green.
- **specification**: `entity/v1/venue.proto` gains an optional `place_id` on reads; `rpc/organizer/series/v1` gains `SearchVenues`. `EventDraft.place_id` became required (**BREAKING** for the console, the only client); it then drops its protovalidate `required`, and `usecase/series/update` requires it only for new and DRAFT events.
- **backend**: `VenueUseCase.Search`, `Venue.SearchPlaces` and `Venue.GetPlace` on the existing Google Places client; venue resolution in draft creation requires a place id and creates new Venues from the catalog's place; the organizer Series handler gains `SearchVenues`; the authored read fills each event's venue and its place id; Update keeps the Venue of a published or cancelled date.
- **Sequencing**: lands after `unify-ticket-sales`, `restructure-event-publishing` and `rename-reception-to-scanner`, and after `ticket-wallet-and-checkin` archives (tasks group 0). The first-come editor shipped with `first-come-ticket-sales`; this change gives it its entries on the Sales tab.
- **Other changes**: `refactor-shared-ui-design-system` is superseded except its admin shell; the owner decides whether to delete it or archive it as superseded (task 0.5).
