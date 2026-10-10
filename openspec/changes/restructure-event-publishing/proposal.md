## Why

An Organizer's concert can only be published as a whole, once. After publish it cannot be corrected and cannot gain dates:

- `ConcertService.Update` is documented as a correction on a published concert, and `Publish` is documented as adding later dates to a published Series. The spec `usecase/series/update-draft` rejects both, and so does the code: every save of a published concert fails with FailedPrecondition. A doors-open time or start time announced after publish cannot be entered, and a tour cannot add 追加公演 (additional dates).
- The draft lives in separate tables (`draft_events`, `draft_series_performers`) that exist only to keep draft rows out of the event natural key. Every rule about publishing is therefore a copy step between two models. Every fan-facing read filters by the Series' state, so one date of a tour cannot be cancelled or kept back on its own.

The pilot Organizer needs to correct published pages and add dates before its first sale. The product has no users yet and only test data, so the cheapest time to move publishing onto the Event is now.

## What Changes

- **Each first-party Event has a publish state**: DRAFT, PUBLISHED or CANCELLED. A discovered Event has none. A draft is an ordinary Event in DRAFT. It holds no slot of the catalog and is not a Concert, so no fan or discovery read sees it.
- **BREAKING** The Series loses its stored publish state. Its displayed state is derived from its Events: Published when one Event is published, Cancelled when none is published and one is cancelled, Draft when all its Events are drafts.
- **BREAKING** `DraftEvent` is removed. Its performances become DRAFT Events, and their performers become the Event's performers.
- **Publish per event.** `Publish` publishes the named DRAFT Events of a Series, or all of them when none is named. A published Series can gain new dates: each starts as DRAFT and is published on its own. The claim, suppressed-slot and other-Organizer rules stay as they are. Followers of a PUBLIC Series are told only about the newly added Events.
- **Corrections after publish.** `Update` accepts a Series with published Events:
  - The title, description, cover image and doors-open time can change.
  - The start time can be set or changed until a TicketSale offers the Event. Changing it applies the slot rules again.
  - The venue and date of a published Event are fixed. To move a date, the operator cancels the Event and adds a new one.
  - Type, source page and visibility are fixed once the Series has a published or cancelled Event. Performers stay changeable (a guest act added after the announcement).
- **Cancel per event.** `Cancel` cancels the named Events or the whole Series. A published Event becomes CANCELLED. A DRAFT Event is removed, never cancelled. A Series left with no Event is removed.
- Fan visibility and the event page are decided per Event: a PUBLISHED Event of a PUBLIC Series is listed, and a CANCELLED Event keeps its event page with the cancellation banner.
- The organizer concert editor keeps working on published concerts: venue and date of published Events are read-only, and new dates show as drafts until they are published. The console redesign is the separate change `redesign-organizer-console`.

## Capabilities

### New Capabilities

- `components/entity/series/update`: replaces a Series' authored content, adding, changing and removing DRAFT Events and correcting PUBLISHED ones, together or not at all
- `components/entity/series/publish-events`: publishes the given DRAFT Events of a Series into the catalog with the claim and slot rules, and returns the ids of the added Events
- `components/entity/series/cancel-events`: cancels the given PUBLISHED Events, removes the given DRAFT Events, and removes the Series when no Event is left
- `components/usecase/series/update`: the owner corrects a concert, published or not (replaces `update-draft`)

### Modified Capabilities

- `components/entity/event` (Purpose and requirements): gains the publish state and its transitions. Identity counts only Events that are not DRAFT. Public visibility moves here from the Series. Venue and date are fixed after publish, and the start time is fixed once a TicketType offers the Event
- `components/entity/series` (Purpose and requirements): loses the publish state, published-at and cancelled-at rows and the DraftEvent relation; gains the derived publish state; the public visibility, draft-catalog and terminal-cancel rules move to the Event; the event-page rule (added by `public-event-page`) becomes per Event; what may change after publish
- `components/entity/series/create-draft` (Purpose and requirement): stores the Events as DRAFT Events with their performers
- `components/entity/series/get-authored` (Purpose and requirement): returns every Event with its publish state, with no draft or live branch
- `components/entity/event/is-event-published` (Purpose and requirement): reads the Event's own publish state
- `components/entity/concert` (Purpose and requirements): a DRAFT Event is not a Concert; a Concert carries its Event's publish state; fan visibility follows the Event
- `components/entity/concert/list`, `list-by-artist`, `list-by-artists`, `list-by-follower`, `list-by-location`: leave out Concerts by the Concert's fan visibility, with a draft or cancelled date of a published Series excluded
- `components/usecase/series/create-draft` (Purpose and requirement): each event is stored as a DRAFT Event
- `components/usecase/series/publish` (Purpose and requirements): publishes named DRAFT Events; a published Series can publish new dates; the share token is set on the first publish only
- `components/usecase/series/cancel` (Purpose and requirements): cancels named Events or the whole Series; drafts are removed; the announcement carries only the cancelled Events
- `components/usecase/concert/get` (added by `public-event-page`): returns the Event's publish state
- `components/infrastructure/fan/web/route/event` (added by `public-event-page`): the cancellation banner follows the Event
- `components/infrastructure/organizer/web/route/concert-editor`: corrections on a published concert and dates added as drafts
- `components/infrastructure/organizer/web/route/concerts`: Publish is offered while a concert has a DRAFT event, published or not
- `stories/publish-an-organizer-concert` (Purpose and requirements): corrections after publish and an additional date on a published concert
- `components/entity/venue` (Purpose only): the erDiagram loses `Venue ||--o{ DraftEvent`

Entity operations that the usecases rely on and that this change does not change: `Series.Get`, `Series.SetUnlistedToken`, `Series.ListByOrganizer` (its DRAFT/PUBLISHED/CANCELLED wording now reads the derived state), `Organizer.ListArtists`, `Venue.GetByPlaceID`, `Venue.GetByListedName`, `Venue.Create`, `TicketSale.ListByEvent` (added by `unify-ticket-sales`), `Event.GetEventStartTime`, `Event.GetOrganizerID`. The other Concert operations (`Create`, `ListByIDs`, `ListEventsBySeries`, `FindEventsByVenueAndDate`, `FindEventsByArtistAndDate`, `FillEventStartTimes`, `DeleteAndSuppress`) are unchanged in their own specs. The new Concert rule "A draft event is not a concert" covers them.

### Removed Capabilities

These are written as REMOVED deltas:
- `components/entity/draft-event`
- `components/entity/series/update-draft` (replaced by `series/update`)
- `components/entity/series/publish-draft` (replaced by `series/publish-events`)
- `components/entity/series/mark-cancelled` (replaced by `series/cancel-events`)
- `components/usecase/series/update-draft` (replaced by `usecase/series/update`)

## Impact

- **specification** (proto, breaking on BSR, `buf skip breaking`):
  - `entity/v1/event.proto` and `concert.proto` gain `publish_state`.
  - `Series.publish_state` becomes derived and output-only.
  - The organizer `ConcertService`: `EventDraft` gains an optional `event_id`, `PublishRequest` and `CancelRequest` gain `event_ids`, and the doc comments of `Update`, `Publish` and `Cancel` are corrected.
- **backend**:
  - One migration: `events.publish_state` is added and filled. `draft_events` and `draft_series_performers` move into `events` and `event_performers`. The full unique constraint `uq_events_natural_key` becomes a partial unique index that skips DRAFT rows. `series.publish_state`, `published_at` and `cancelled_at` are dropped.
  - Series repository: create, update, publish, cancel and get-authored.
  - Concert repository: one shared catalog condition and one fan-visibility condition replace the Series-state guard.
  - `EventPublishStateRepository`.
  - `ConcertAuthoringUseCase` and the organizer handler.
  - `Series.IsPubliclyVisible` and `Series.HasEventPage` move to the Event.
- **frontend**:
  - Organizer concert editor, concert list and reception links screen: read the per-Event state.
  - Fan event page: the banner follows the Event.
- **Other in-flight changes**: `unify-ticket-sales` and `public-event-page` land first. `organizer-event-authoring-extensions` (scheduled publish) and `redesign-organizer-console` build on this change. See design.md "Sequencing".
- **Production data**: only test data. The rows to migrate are counted read-only first.
