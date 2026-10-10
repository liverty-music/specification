## Why

A Concert read repeats data and mixes two levels of the model:

- **Repeated data.** Every returned Concert embeds its whole Series. Since `public-event-page`, that includes the description (up to 10,000 characters). A ten-date tour therefore sends the same Series ten times in one list.
- **Event page.** The page calls `Get` and then `ListBySeries`, and receives the Series once per date.
- **Generic and music data mixed.** The generic Event already carries the performing Artists in the spec, and the organizer API calls a whole Series a "concert" (`AuthoredConcert`).

Fan club events are a planned second kind of event. Before one arrives, the model has to keep the generic Event free of music data. The product has no users yet, so changing the API shape now is cheap.

## What Changes

- **Naming rule.**
  - Generic things are named Event or Series; music-specific things are named Concert.
  - A future kind, such as a fan club event, gets its own type that holds an Event, as a Concert does.
  - Discovery (`StagedConcert`, `CONCERT.*` subjects, the `concert-discovery` job), notification types, analytics names and the `/concerts/:id` URL stay as they are: they are about concerts.
- **BREAKING** `entity.v1.Concert` becomes `{ event: Event, artist_ids }`:
  - It no longer embeds its Series or the Artists.
  - It reaches its Series through `event.series_id`.
  - `entity.v1.Event` gains `listed_venue_name`, and it carries no Artists.
- **BREAKING** Every response that returns Concerts also carries each referenced Series and Artist exactly once (`series`, `artists`). This applies to:
  - the fan `ConcertService`;
  - the organizer `SeriesService`;
  - the admin `ConcertService.List`.
- **One Series shape on every read.** Each returned Series carries its organizer id, description, cover image, visibility and publish state when it has them. A list therefore shows the same Series as the event page does.
- **BREAKING** The organizer `ConcertService` becomes `SeriesService`:
  - Each of its eight RPCs acts on a Series.
  - `AuthoredConcert` is removed; its RPCs return `{ series, concerts, artists }`.
- **BREAKING** The fan RPC `ConcertService.SearchNewConcerts` is removed:
  - No client calls it, and it lets an unauthenticated caller start a paid Gemini search.
  - The usecase stays: the discovery job and the first-follow consumer call it in process.
  - The fan API's 120-second limit for concert calls existed only for this RPC, so every fan call now gets the 30-second limit.
- The performer link moves off the generic Event:
  - The table `event_performers` becomes `concert_artists`, keyed by the Concert (`concerts.event_id`) instead of the Event.
  - The `concerts` table stays as the music extension of `events`.

## Capabilities

### New Capabilities

None. The organizer boundary keeps its requirements under a new path (below).

### Modified Capabilities

- `components/entity/event` (Purpose): the performers attribute and the Artist relation leave the Event. The requirement "Performers of an event" is removed; a Concert's Artists replace it.
- `components/entity/concert` (Purpose): a Concert is an Event plus the ids of its performing Artists. It reaches its Series through the Event and no longer embeds it. The requirement "A concert is exactly one event" changes to match.
- `components/adapter/fan/api/rpc/concert`: changes in three places.
  - SearchNewConcerts leaves the public calls and the boundary validation.
  - Returned Concerts come with each referenced Series and Artist once.
  - Every returned Series carries its cover image.
- `components/adapter/admin/api/rpc/concert`: List returns each referenced Series and Artist once.
- `components/adapter/organizer/api/rpc/series`, today `components/adapter/organizer/api/rpc/concert`:
  - The main spec moves to the new path in a direct commit on the main specs before this change merges. The commit carries the mapping table, as the spec-tree rules require for a move.
  - The service is named the organizer Series service.
  - List returns Series with their Concerts.
  - A new requirement states what a returned Series carries.
- `components/infrastructure/fan/api/server/request-timeout`: every fan call gets 30 seconds, now that no concert call runs a search.
- `components/usecase/concert/get`: Get reads the Series, cover image included, through Concert.ListByIDs instead of a second Series.Get (design D3), so a Series.Get failure no longer applies.

Unchanged, and relied on:

- The usecases (`components/usecase/concert/*` other than `get`, `components/usecase/series/*`) keep their behavior. They still return Concerts with their Series and Artists; only the wire shape changes at the boundary.
- `components/entity/concert/create` keeps its promise. It reports new Events and newly linked Artists through the same `concerts` insert and artist link.
- The Concert read operations (`list`, `list-by-ids`, `list-by-follower`, `list-by-artists`, `list-by-location`, `list-by-artist`) still return each Concert with its Venue, Series and performing Artists. Their Series additionally carries the cover image; this is a read detail, not a change of promise.
- `components/entity/series` and its operations.
- The fan, admin and organizer web route specs: no screen behaves differently.

## Impact

- **specification (proto):**
  - `entity/v1/concert.proto` and `event.proto`.
  - The fan, organizer and admin concert services: the organizer one moves to `rpc/organizer/series/v1`.
  - A Release and BSR generation.
- **backend:**
  - The mappers build the `series` and `artists` lists.
  - The Concert reads add the Series' cover image.
  - The organizer handler moves to the Series service, registered in `internal/di/provider.go`.
  - The fan `SearchNewConcerts` handler and its public-procedure entry are removed, along with `SERVER_CONCERT_HANDLER_TIMEOUT`.
  - An Atlas migration renames `event_performers` to `concert_artists` and re-points its foreign key at `concerts`. The organizer-console-api grants and their integration test follow.
- **frontend:**
  - The fan `ConcertStore`, the event page and the tickets page read the new shape.
  - The admin approved-concerts screen and the organizer console client move to it too.
  - The test mocks and the e2e fixtures of the ConcertService shape are updated.
- **cloud-provisioning:** `SERVER_CONCERT_HANDLER_TIMEOUT` leaves the fan-api ConfigMap after the backend release.
- **Changes in flight:** a follow-up rewrites their artifacts to the new names (`concert_artists`, organizer `SeriesService`, `Concert { event, artist_ids }`):
  - `restructure-event-publishing`
  - `redesign-organizer-console`
  - `migrate-discovered-sales`
  - `unify-ticket-sales`
  - `organizer-event-authoring-extensions`
