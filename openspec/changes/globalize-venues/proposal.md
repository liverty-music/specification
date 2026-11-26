## Why

Venues and concerts outside Japan are already part of the product (discovery stores overseas venues, and Japanese artists' tours regularly include shows abroad), but the model behind them assumes Japan. The admin area design of 2026-02 (archive `2026-02-22-extract-concert-venue`, `2026-02-28-normalize-admin-area`, `2026-03-11-nearby-proximity-filter`) chose ISO 3166-2 codes, a deterministic conversion from text, "a wrong area is worse than none" and HOME as an equal area; those principles stay. What was left unfinished, or assumed Japanese, now causes harm in production (read-only, 2026-11-11 and 2026-11-24):

- **Any well-formed area code is accepted.** The rule that a Home's level 1 is a *known* ISO code (2026-02-28) was never implemented; `JP-99` and codes an LLM invents are stored for Venues and Homes alike.
- **One area is stored at different levels.** 9 lower-level codes on 12 Venues (`FR-33`, `GB-LIV`, `BE-VOV`) never equal the first-level code a Home or another Venue carries, so HOME misses them; `FR-75` (3 Venues) is a code ISO withdrew.
- **35% of Venues have no area.** 303 of 876 Venues (474 Events), mostly overseas. The text-to-code table covers Japan only, and a place with no subdivision code of its own (Hong Kong, Macau) cannot get an area at all.
- **Every Venue is in Japan time.** The living spec says every Venue's time zone is Asia/Tokyo (`entity/venue` "Current date at a venue", liverty-music/specification#1379). The organizer console turns an entered start time into an instant as Japan time, so 18:30 at a venue in Seoul or London is stored as 18:30 in Tokyo; fan and organizer screens show every time in Japan time; and day boundaries for overseas Events are off by the time difference.
- **Future times are stored as instants.** Event start and open times and sale windows are stored as absolute instants. If a country changes its time-zone rules before the date (Mexico abolished daylight saving time in 2022 at a few weeks' notice), the stored instant no longer matches the wall-clock time the organizer or the source announced.
- **Google Maps content is stored without limit.** Venue coordinates and the names of resolved Venues come from Google Places and are kept forever, and so are the resolved name and coordinates of every ConcertCandidate. The Google Maps Platform terms allow Places coordinates for 30 days and forbid saving business names (ToS §3.2.3(a)(iii), Service Specific Terms §14.3).
- **Area facts are scattered and disagree.** Centroids sit in a Go table and in a different frontend table (Tokyo: 35.6894, 139.6917 in the backend, 35.686, 139.556 in the frontend), the fan app builds the reference point of ConcertUseCase.ListByLocation itself, and the location search's candidate box only holds for Japan's latitudes. A Home is a separate `homes` row that outlives a deleted User (4 such rows).

## What Changes

- **Area reference data.** An Area is a first-level subdivision from the published ISO 3166-2 list, loaded from a pinned release of a maintained dataset, with its English and Japanese names, a reference point and how it was obtained, and its time zone when the whole Area has one. Lower-level and withdrawn codes are kept only so that they resolve to their first-level Area. A country or territory with no subdivision of its own (Hong Kong, Macau) is its own first-level Area. A **region** (Japan's eight 地方, such as 関東) is an Area that groups first-level Areas, separately from the administrative hierarchy. The time zones of each country come from a pinned release of the IANA time zone database.
- **Area.Resolve** turns a code (first-level, lower-level or withdrawn, any letter case) or an English or Japanese name into exactly one first-level Area; anything else is NotFound.
- **A Venue's admin area and a Home are the code of a first-level Area.** **BREAKING (spec):** a well-formed code that is no first-level Area is now invalid.
- **Every Venue has an admin area and a time zone.** The time zone is an IANA name of the Venue's country, taken from its Area when the Area has one zone, else from the source, the admin or the member. Discovery stages an event whose area or time zone does not resolve; the admin can give or correct both when approving.
- **The organizer confirms the venue's name, country, area and time zone.** After a member picks a place, the editor fills in the place's name, country, suggested area and time zone; the member edits or confirms them, and what the member saves is stored. The time zone is always shown, next to every time the member enters.
- **Future wall-clock times are stored as wall-clock times.** An Event's start and open times are times of day at its Venue, and a TicketSale's start and end are local date-times in the sale's time zone; instants are computed from them when a rule needs one. Moments in the past (a find time, a scan, a login) stay instants. **BREAKING (proto):** `StartTime` and `OpenTime` carry a time of day, and a TicketSale's window carries local date-times with a time zone.
- **Every Event rule uses its Venue's time zone.** The current date at a Venue, the admission window, the resale draws and deadline, and the lists of upcoming Events are computed in the Venue's own time zone, one row at a time in queries. This closes liverty-music/specification#1379.
- **Times are shown in the zone they belong to.** An Event's date and times are shown at its Venue's local time, labelled when the viewer is in another zone, with the viewer's own time beside them on fan screens. A sale window is shown to a fan in the fan's own time zone and to a member in the sale's time zone, labelled. The organizer console no longer shows every time as JST.
- **Google place data is a cache.** A Venue keeps its place id; its coordinates are stored with the time they were fetched, refreshed by a daily job before they are 30 days old, and removed when they expire. A Venue's name is the name its source listed or the name a member saved, never a name taken from Google. A ConcertCandidate keeps only the resolved place id.
- **Existing data is completed.** Lower-level and withdrawn codes are replaced by their first-level Area; Venues without an area or a time zone are completed by a Gemini estimate from the listed venue name and source page, then by the owner; the five pairs of Venues sharing a listed name are reviewed one by one before any merge; existing start, open and sale times are converted to wall-clock times in their Venue's or sale's zone; then the columns become required.
- **A Home is owned by its User.** The `homes` table and the Home id go away, a deleted User leaves no Home behind, and a Home is stored so that a second one can be allowed later without a new table. **BREAKING (spec, proto field removal):** level 2 (empty in all 11 production Homes) and `Home.centroid` (filled by no response) are removed.
- **The server resolves reference points.** ConcertUseCase.ListByLocation takes an area, and the server uses its Area's reference point; the frontend's centroid table goes away. **BREAKING (proto):** `ListByLocationRequest.location` is replaced by an area and `entity.v1.GeoLocation` is removed.
- **The location search works at any latitude.** The candidate box around a reference point is sized from its latitude and wraps across the antimeridian.
- Out of scope: the fan home-area selector, which keeps its own prefecture and region list (separate issue); localized names for overseas areas on fan screens (separate issue); notification times, which already use the fan's time zone; the schedules of the backend's daily jobs, which stay in Japan time.

## Capabilities

### New Capabilities

- `components/entity/area`: the Area reference data, what a first-level Area and a region are, an Area's time zone.
- `components/entity/area/resolve`: the first-level Area a code or a name stands for.
- `components/entity/area/list-by-country`: the first-level Areas, regions and time zones of one country.
- `components/entity/area/list-countries`: the countries that have first-level Areas, with their names.
- `components/usecase/area/list-countries`: a member lists the countries to choose a venue's country from.
- `components/usecase/area/resolve`: an admin resolves an entered area to its first-level Area, to choose its time zone.
- `components/entity/venue/get-place-coordinates`: read only a place's coordinates, for the refresh and approval.
- `components/usecase/area/list-by-country`: a member lists the Areas and time zones to confirm a venue from.
- `components/usecase/venue/resolve-place`: a member reads a picked place as the Venue that holds it, or as a name, country, area and time zone to confirm.
- `components/usecase/venue/refresh-coordinates`: the daily refresh and expiry of cached coordinates.
- `components/entity/venue/set-coordinates`: store a Venue's coordinates with their fetch time.
- `components/entity/venue/list-coordinates-due`: the Venues whose coordinates are missing or due for a refresh.
- `components/entity/venue/clear-expired-coordinates`: remove coordinates older than 30 days.
- `components/adapter/organizer/api/rpc/area`: the organizer Area service boundary.
- `components/adapter/admin/api/rpc/area`: the admin Area service boundary, for the approval queue's time zone choice.

### Modified Capabilities

Areas and Homes:

- `components/entity/user` (Purpose): the Home attribute table loses `id`, `level 2` and the stored centroid; a Home is a first-level Area.
- `components/entity/user`: "Home validation" is replaced by "A Home names a first-level Area".
- `components/entity/user/create`: "Create sets the home's centroid" is replaced by "A created Home names its Area".
- `components/entity/user/update-home`: both requirements are replaced (no Home id, no level 2, no stored centroid).
- `components/entity/user/delete`: the Home is removed with the User.
- `components/entity/user/get`, `components/entity/user/get-by-provider-user-id`: a returned Home carries its Area's reference point, not a stored centroid.
- `components/entity/coordinates` (Purpose): coordinates are a Venue's location or an Area's reference point, no longer a Home's centroid.
- `components/entity/user/resolve-centroid`: removed; an Area carries its reference point.
- `components/usecase/user/set-home`: a home that is no first-level Area fails with InvalidArgument.
- `components/usecase/concert/list-by-artists`: the home's reference point is its Area's.
- `components/usecase/concert/list-by-location`: takes an area; fails with InvalidArgument for one that is no first-level Area; finds venues near reference points at any latitude.
- `components/entity/concert/list-by-location`: candidates within 200 km at any latitude and across the antimeridian; only same-area candidates for an Area without a reference point.
- `components/entity/geo-location` (Purpose and validation): the reference point is the given Area's, resolved by the server.
- `components/infrastructure/fan/web/route/discovery`: the Concerts view sends its area code, not a point built from a centroid.
- `components/adapter/fan/api/rpc/user`: a returned Home carries neither level 2 nor a centroid.
- `components/adapter/fan/api/rpc/concert`: ListByLocation takes an area; an Event carries its local times and its Venue's time zone.

Venues and Google place data:

- `components/entity/venue` (Purpose, "Admin area format", "Canonical name falls back to the listed name", "Current date at a venue", "Listed venue name normalization"): the admin area and the time zone are required; the name is the listed or member-saved name; coordinates are a cache at most 30 days old; the current date at a Venue is computed in its own time zone; "private" and "private event" are names of no venue, like "TBA".
- `components/entity/venue/create`: fails without a first-level admin area or a time zone of the Area's country; stores coordinates with their fetch time.
- `components/entity/venue/get-by-listed-name`: an admin area is required; the absent-matches-absent rule goes.
- `components/entity/venue/get-place`: returns the place's name, country, coordinates, the area its address suggests and its time zone, for a member to confirm.
- `components/entity/concert/search`: returns a first-level Area code and local start and open times; leaves out private events and shows on a ship or at sea.
- `components/usecase/concert/create-from-discovered` (and Purpose diagram at archive): stages an event without an admin area or time zone; a new Venue takes the listed name; a candidate keeps only the resolved place id.
- `components/usecase/concert-candidate/approve` (and Purpose diagram at archive): takes the area and time zone from the admin when the candidate lacks them; fetches the place's coordinates by place id.
- `components/usecase/series/create`: a new place's Venue gets the name, area and time zone the member saved.
- `components/adapter/organizer/api/rpc/venue`: ResolvePlace is gated like Search.
- `components/adapter/admin/api/rpc/concert-candidate`: Approve passes the admin's area and time zone; a candidate carries its area, time zone and resolved place id, not a resolved name or coordinates.

Times:

- `components/entity/event` (Purpose and a new requirement): start and open times are times of day at the Venue; a time in a daylight-saving gap is invalid and a repeated time is the earlier instant.
- `components/entity/event/get-event-start-time`: returns the start time with the local date and the Venue's time zone.
- `components/entity/concert/list-upcoming-by-artist`: each Venue carries its time zone, and "today" is read in it.
- `components/entity/concert-candidate` (Purpose and requirements): times of day at the venue; it keeps only the resolved place id, with its discovered area and time zone.
- `components/entity/discovered-series`, `components/entity/rejected-concert` (Purpose): start and open times are times of day at the venue, with a time zone; a rejected concert keeps only the resolved place id, not a resolved name or admin area.
- `components/usecase/concert/list-followed`, `components/infrastructure/fan/web/route/timetable`: without a from-date, each concert's Venue's current date is the boundary; the Timetable no longer sends the device's date.
- `components/entity/ticket-sale` (Purpose and "result date"): a sale has a time zone, and its start and end are local date-times in it.
- `components/entity/ticket-sale/set-window`, `components/usecase/ticket-sale/set-window`, `components/usecase/ticket-sale/create`: a window carries its time zone, which is one of the sale's events' Venues' zones; a Lottery's length is counted on local date-times.
- `components/usecase/ticket-sale/discover-for-artist`: each series is searched with the time zone its Venues share.
- `components/entity/ticket-sale/upsert-discovered`: the same sale is matched by its start date in the sale's time zone.
- `components/entity/ticket-sale/search-published-sales`: a sale's window is returned as local date-times with the time zone the page states.
- `components/entity/resale-entry`: the daily resale draw runs at 12:00 in the event's Venue's time zone.
- `components/adapter/organizer/api/rpc/ticket-sale`: Create and SetWindow take local date-times and a time zone.
- `components/adapter/fan/api/rpc/ticket-sale`: a TicketSale carries its window as local date-times with its time zone.
- `components/infrastructure/organizer/web/global/i18n` (Purpose and requirements): "Dates and times in Japan time" is replaced by times shown in the zone they belong to, labelled.
- `components/infrastructure/organizer/web/route/concert`: each event's date and start time at its venue's local time, labelled.
- `components/infrastructure/organizer/web/route/concert-editor`: "Event times are entered in Japan time" is replaced by entry at the venue's local time, with the zone and, for a venue abroad, the Japan time shown; the member confirms the prefilled name, country, area and time zone of each new place.
- `components/infrastructure/organizer/web/route/ticket-sale-editor`: "A lottery window is entered in Japan time" is replaced by entry in the sale's time zone, defaulting to its events' venue zone.
- `components/infrastructure/organizer/web/route/event` and `components/infrastructure/organizer/web/route/home`: event times at the venue's local time and sale windows in the sale's time zone, labelled.
- `components/infrastructure/fan/web/global/i18n`: a new requirement on which zone each kind of time is shown in.
- `components/infrastructure/fan/web/route/concert`: event times at the venue's local time with the fan's own time beside them when the zones differ; sale windows in the fan's time zone.
- `components/infrastructure/fan/web/global/link-preview`: times at the venue's local time with its zone.
- `components/infrastructure/fan/web/global/legal-document`, `components/infrastructure/fan/web/route/tickets`: the resale draw time is 12:00 at the venue's local time.
- `components/infrastructure/admin/web/route/approval-queue`: the admin gives or corrects the area and time zone of any candidate; the resolved place is shown as a map link.

Unchanged, and why: `components/entity/concert` "Proximity to a home area" and `components/entity/proximity` compare the same codes, now always first-level, and NEARBY already falls back to AWAY without coordinates; the Event and Concert operations that compare "Venue, date and start time" (`entity/concert/create`, `fill-event-start-times`, `entity/series/publish-events`, `filter-new-series` and others) keep their wording, now over local times; `entity/scanner` and `entity/resale-listing` already use the Venue's time zone; `entity/settlement` reads the start time as an instant, which is now computed; `entity/notification` already uses the fan's time zone; `entity/concert/list-by-follower` already compares with "the current date", which `entity/venue` now defines per Venue; `entity/venue/search-place` returns each place's country and first-level Area, and `select-place` picks only places inside the event's admin area (Decision 19); both still store none of Google's content.

## Impact

- backend: `areas`, `area_memberships` and `country_time_zones` with their generator and seed migration; `venues.admin_area` normalized, completed and constrained; `venues.time_zone`; `venues.coordinates_fetch_time` and the `venue-coordinates-refresh` job; Venue names replaced by listed names; `events.local_start_time` and `local_open_time` replacing `start_time` and `open_time`; `ticket_sales.time_zone`, `local_start_time` and `local_end_time` replacing the instants; the same for `concert_candidates` and `rejected_concerts`, which also lose the resolved name, coordinates and admin area; `user_home_areas` replacing `users.home_id` and `homes`; `entity.Area`, `AreaRepository`; `entity.VenueTimeZone` taking a Venue; every Event-day rule and query per Venue zone; the Gemini searcher asking for local times and time zones; a one-off backfill command using Gemini.
- specification: proto `entity/v1.Venue.time_zone`; `StartTime` and `OpenTime` as `google.type.TimeOfDay`; TicketSale windows as `google.type.DateTime` with a time zone; `entity/v1.Home` (`level_2` and `centroid` reserved); `entity/v1.GeoLocation` removed; `ListByLocationRequest`; `entity/v1.Area`, `AreaQuery`; the organizer and admin `AreaService.ListByCountry`, `VenueService.ResolvePlace`, `EventDraft.admin_area` and `time_zone`, the admin ConcertCandidate and `ApproveRequest` changes.
- frontend: time formatting in the fan app and the organizer console (venue-local, sale and viewer zones, labels), the organizer editors' time zone display and inputs, the organizer venue confirmation, the admin approval queue, the fan Concerts view sending an area, removal of `JP_PREFECTURE_CENTROIDS`, the `Asia/Tokyo` constants and `level2`.
- cloud-provisioning: the `venue-coordinates-refresh` CronJob.
- Google Maps Platform: this change assumes that a name, area and time zone prefilled from Places and saved by a member may be stored (design Risks); Place Details calls for the refresh.
- Data: no Venue loses an area; no identity collision (checked read-only); every stored time keeps the wall-clock time it was announced at; the 4 orphaned Homes go with `homes`.
