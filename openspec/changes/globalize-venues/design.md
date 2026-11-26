## Context

See proposal.md (Why) for the problems. The code this change replaces (backend `origin/main`, re-checked 2026-11-24):

- `geo.NormalizeAdminArea` (`internal/infrastructure/geo/normalize.go:21-35`) passes any well-formed code through upper-cased and maps the 47 Japanese prefecture names (`entity.PrefectureCode`). The Gemini searcher and the organizer `GetPlace` (`internal/infrastructure/maps/google/catalog.go:160-170`, from the place's `administrative_area_level_1`) call it.
- Google place data is stored without limit: `GetPlace` returns the place's `displayName` and location (`catalog.go:160-162`), `SeriesUseCase` stores both as the new Venue's name and coordinates (`internal/usecase/series_uc.go:276-282`), discovery stores the place it selects the same way, and `concert_candidates` keeps `resolved_venue_name`, `resolved_latitude` and `resolved_longitude` (`schema.sql:409-413`).
- A Home is a `homes` row referenced by `users.home_id` (`ON DELETE SET NULL`), so a deleted User leaves its row behind. Its centroid is copied from a Go table of the 47 prefectures; the frontend has a second, different table (`src/entities/user.ts:114-165`) from which the fan Concerts view builds the `GeoLocation` it sends to ListByLocation (`src/components/discovery-concerts/discovery-concerts.ts:199`).
- The location search reads a box of ±1.8° latitude and ±2.6° longitude around the reference point first (`internal/entity/geo_location.go:32-40`), wide enough for 200 km only up to 46°N.
- Every Venue is in Asia/Tokyo: `entity.VenueTimeZone()` returns it for all (`internal/entity/venue.go:147`), with callers in the scanner and resale rules. `events.start_time` and `open_time` and `ticket_sales.start_time` and `end_time` are `TIMESTAMPTZ`. The organizer console composes an entered date and time as Japan time (`organizer/concert-editor/concert-form.ts:155-171`, `parseJstDateAndTime`), the fan app formats event and sale times in `Asia/Tokyo` (`EVENT_TIME_ZONE`, `src/routes/concert/concert-page.ts:7`, and 14 other files), and the Gemini searcher takes start times as RFC 3339 with an offset (`searcher.go:1078-1080`). Resale draws are found by a workflow that runs every minute (`DrawResaleSchedule`, `resale_draw_workflow.go:18`).
- Read-only production facts (2026-11-11), from which the migration numbers below come: 876 Venues, 303 with no admin area (296 with a place id and coordinates; 267 overseas, 29 near Japan or Korea, 7 with no coordinates; 474 Events on them); 153 distinct codes, of which 143 are first-level (558 Venues), 9 lower-level (12 Venues) and `FR-75` withdrawn (3 Venues); no `(listed_venue_name, admin_area)` collision once every code is first-level; 5 listed names held both by a Venue with an area and by one without (Zepp Haneda, Zepp Fukuoka, Zenith, MilkBoy, Grand Theatre at The Grand Sierra Resort); 11 `homes` rows, none with `level_2`, 7 referenced by a User.

## Goals / Non-Goals

**Goals:**

- One stored vocabulary for every area: the code of a first-level Area, enforced by the database on every stored reference, in a key space that can take regions and finer areas later without changing what a stored code means.
- Reference data (areas and time zones) reproducible from pinned public releases, updated by one generated migration, checked for new releases on a schedule, and never losing a referenced value.
- Every Venue in its own IANA time zone, and every future wall-clock time stored as the wall-clock time that was announced.
- Every time shown in the zone it belongs to, labelled, in both web apps.
- Google place data kept only as the terms allow: place ids indefinitely, coordinates for at most 30 days, names, areas and time zones only as a member saved them.
- One place where an area becomes a point: the server.

**Non-Goals:**

- A lower-level area on Homes or Venues (the old level 2). The `areas` rows of lower levels exist only so that Resolve can map them up.
- More than one Home per User. The storage allows it; the rules, screens and proximity for several Homes are a later change.
- Localized area names on fan screens, and the fan home-area selector reading regions from the server (separate issues).
- Times that are already right: notification texts use the fan's time zone (`entity/notification`); the daily jobs' schedules are operational and stay in Japan time; moments in the past (find, scan, login, payment) stay instants.

## Decisions

### 1. Reference tables keyed by standard codes: areas and time zones

```sql
CREATE TABLE time_zones (
  name TEXT PRIMARY KEY,                         -- IANA: 'Asia/Seoul'
  name_en TEXT NOT NULL,                         -- CLDR exemplar city: 'Seoul'
  name_ja TEXT                                   -- 'ソウル'
);
CREATE TABLE country_time_zones (
  country_code TEXT NOT NULL,
  time_zone TEXT NOT NULL REFERENCES time_zones (name),
  PRIMARY KEY (country_code, time_zone)
);
CREATE TABLE areas (
  code TEXT PRIMARY KEY,                         -- 'JP-13', 'FR-33', 'HK', 'JP-KANTO'
  kind TEXT NOT NULL,                            -- 'subdivision' | 'country' | 'region'
  country_code TEXT NOT NULL,                    -- 'JP'
  parent_code TEXT REFERENCES areas (code),      -- NULL for first-level
  replaced_by_code TEXT REFERENCES areas (code), -- NULL while current
  name_en TEXT NOT NULL,
  name_ja TEXT,
  reference_latitude DOUBLE PRECISION,
  reference_longitude DOUBLE PRECISION,
  reference_point_source TEXT,                   -- see Decision 2
  time_zone TEXT,                                -- set only when the whole Area has one zone
  is_first_level BOOLEAN GENERATED ALWAYS AS
    (kind <> 'region' AND parent_code IS NULL AND replaced_by_code IS NULL) STORED,
  CONSTRAINT uq_areas_code_first_level UNIQUE (code, is_first_level),
  CONSTRAINT fk_areas_time_zone FOREIGN KEY (country_code, time_zone)
    REFERENCES country_time_zones (country_code, time_zone),
  CONSTRAINT chk_areas_code CHECK (
       (kind = 'subdivision' AND code ~ '^[A-Z]{2}-[A-Z0-9]{1,3}$')
    OR (kind = 'country'     AND code ~ '^[A-Z]{2}$')
    OR (kind = 'region'      AND code ~ '^[A-Z]{2}-[A-Z]{4,}$')),
  CONSTRAINT chk_areas_country CHECK (left(code, 2) = country_code),
  CONSTRAINT chk_areas_reference_point CHECK (
        (reference_latitude IS NULL) = (reference_longitude IS NULL)
    AND (reference_latitude IS NULL) = (reference_point_source IS NULL))
);
CREATE INDEX idx_areas_name_en ON areas (lower(name_en));
CREATE INDEX idx_areas_name_ja ON areas (name_ja);

CREATE TABLE area_memberships (
  region_code TEXT NOT NULL REFERENCES areas (code),
  member_code TEXT NOT NULL,
  member_first_level BOOLEAN NOT NULL DEFAULT TRUE CHECK (member_first_level),
  PRIMARY KEY (region_code, member_code),
  FOREIGN KEY (member_code, member_first_level) REFERENCES areas (code, is_first_level)
);
```

The code is the identity, as Google AIP-143 recommends standard codes over invented ids for regions, languages and time zones (IANA names in a field called `time_zone`). An area code is not limited to ISO 3166-2: a country or territory with no subdivision of its own is a `country` row whose code is its ISO 3166-1 code (`HK`, `MO`), and a region is a `region` row whose code has a suffix of four or more letters (`JP-KANTO`), which ISO 3166-2 never uses (its suffixes have one to three characters), so the two cannot collide. A city row can be added the same way later without changing what an existing code means.

"First-level" is a stored generated column, not a rule in the application: `venues` and `user_home_areas` reference `(code, is_first_level)` with a constant `TRUE` column on their side, so the database rejects a lower-level, withdrawn or region code on any write, including a migration or a hand-written statement, with no trigger function (`schema.sql` cannot hold one, #765). A generator run that makes a referenced code stop being first-level fails on that foreign key, which forces the remap of Decision 2. Regions are a separate relation, not a parent: 関東 contains 東京都 for grouping, and 東京都 still has no administrative parent. Japan's eight 地方 are the only regions seeded; the organizer's area list reads them (Decision 6).

Alternatives: a Liverty UUID per Area with codes as external identifiers (rejected: every read joins an identifier table, and a code rename is handled by `ON UPDATE CASCADE` on the code, while splits and mergers need a reviewed remap under either key); a Go table embedded in the binary (rejected: the database could not reject a bad value written by a migration or by hand); a separate table of eligible codes as the foreign key target (rejected: a second copy of the first-level rule that the generator must keep in step).

### 2. Generated from pinned CLDR and IANA releases, with an owned update check

A Go generator (`scripts/areas`, run with `go run`) reads a pinned CLDR release (Unicode License v3) and a pinned IANA time zone database release (public domain):

- Areas: `common/supplemental/subdivisions.xml` for the hierarchy (a code contained directly by a country is first-level), `common/supplemental/supplementalMetadata.xml` `subdivisionAlias` for replacements, `common/subdivisions/{en,ja}.xml` for names. A territory that `subdivisions.xml` gives no subdivisions becomes a `country` row with its CLDR territory name.
- Time zones: `zone.tab` gives the zones of each country, one line per country and zone, so a country keeps a zone named for it (`NL Europe/Amsterdam`) even where `zone1970.tab` merges it into another country's (`Europe/Brussels`); the names are CLDR's exemplar cities (`common/main/{en,ja}.xml`), except where `manual_time_zone_names.csv` overrides them (it starts with `Asia/Tokyo,Japan,日本`, so labels read 日本時間, not 東京時間). An Area's `time_zone` is set when its country has exactly one zone, or from `manual_area_time_zones.csv` for an Area of a several-zone country that lies wholly in one zone (it starts with the US states, Canadian provinces, Australian states, Brazilian states and Mexican states that do); otherwise it stays NULL.

A place that CLDR lists both as a territory without subdivisions and as a subdivision of another country (`HK` and `CN-HK`, `MO` and `CN-MO`, `PR` and `US-PR`, `GU` and `US-GU`) is one Area: the territory's `country` row, with the subdivision code as a replacement pointing to it, as a source may use either code. A place that CLDR lists both as a territory with subdivisions of its own and as a subdivision of another country (`TW`, with `TW-TPE` and 21 more, and `CN-TW`) has no single first-level Area to point to: the subdivision code is left out of the seed (no `areas` row), so `Resolve("CN-TW")` and `Resolve("Taiwan")` are NotFound, no foreign key can accept it, and the Area comes from the place (`TW-TPE`) or the organizer's choice. Each such code is decided in `manual_replacements.csv`, whose rows are `code,decision,target` with three decisions: `replace` (the code becomes a `replaced_by_code` to `target`), `omit` (the code gets no row) and `distinct` (the code and the territory are different places; both stay as generated). The generator fails, unless the code has a row, when a subdivision's English or Japanese name equals the same-language name of a `country` row, or when a CLDR alias's code is the subdivision's code and its replacement is a territory (`uspr → PR`, `usgu → GU`). It does not compare with territories that have subdivisions, so places that only share a name (`US-GA` Georgia and `GE` Georgia) never stop it; `CN-TW` is caught by no rule and is in the file because it was decided here. Aliases are interpreted, not copied: an alias whose replacement is a subdivision code is a `replaced_by_code`; an alias whose replacement is a territory code (`cn91 → HK`, `fi01 → AX`) maps to that territory's `country` row when one exists and is otherwise left out; an alias with several replacements is left out. Hand-kept files in the same directory add what the sources lack or what the product decides: `manual_replacements.csv` (`replace` for `FR-75 → FR-IDF`, `CN-HK → HK`, `CN-MO → MO`, `US-PR → PR` and `US-GU → GU`, so a venue in Hong Kong or Macau has the same area whichever code a source uses; `omit` for `CN-TW`; the US territories `US-AS`, `US-MP`, `US-UM` and `US-VI` are decided the same way when the generator first runs), `manual_reference_points.csv`, `manual_area_time_zones.csv`, and `regions.csv` (Japan's eight 地方 with their member prefectures, copied from the fan app's `REGION_GROUPS`).

Reference points, in order, each recorded in `reference_point_source`: `legacy_prefecture_table` (the current Go table for the 47 prefectures, so no Home's NEARBY result changes); `natural_earth_label` (the label point of the same code in Natural Earth 1:10m admin-1, public domain, pinned release); `natural_earth_children` (the spherical mean of the label points of the Natural Earth features whose CLDR parent chain ends at the Area, for `FR-IDF`, `GB-ENG` and 136 more); `manual` (`manual_reference_points.csv`, starting with `CZ-10`, `GR-I`, `MX-CMX`, `PE-LMA`, `PL-12`, `HK`, `MO`); otherwise none. A reference point is where NEARBY measures from, not a geographic centroid.

The generator writes one Atlas migration of `INSERT ... ON CONFLICT DO UPDATE` statements and never deletes. Before writing, it fails when a code or zone of the previous seed is missing from the new one, or when a code that was first-level stops being first-level; the upgrading change then adds an explicit remap of the affected Venues, Homes and sales. The Go binary's `time/tzdata` and PostgreSQL's zone data are upgraded with Go and Cloud SQL; the generator's pin only decides which zones may be chosen. A weekly GitHub Actions workflow in the backend repository compares the pinned CLDR and IANA tags with their latest releases and opens one issue, assigned to the repository owner, when either is newer. Alternatives: Debian iso-codes (rejected: no hierarchy-to-replacement data and weak Japanese names); ISO's own collection (rejected: a paid licence, while CLDR's subdivision data is generated from it); IANA `zone1970.tab` (rejected: it lists one canonical zone for countries that share clock history, so the Netherlands' only zone would be `Europe/Brussels` and its Venues would be labelled with Brussels' name; Go's `time/tzdata` keeps the per-country names as links, so they load).

### 3. Resolve: one lookup for codes and names, exactly one answer

`entity.AreaRepository.Resolve(ctx, text string, country *string) (*Area, error)`, implemented in `rdb`:

1. Trim; empty → InvalidArgument.
2. A text matching a code pattern case-insensitively is looked up by `upper(text)`.
3. Otherwise by `lower(name_en) = lower(text)`, or `name_ja` equal to the text or to the text plus 都, 道, 府 or 県; restricted to `country_code` when given. Region rows are never matched.
4. Each match follows `replaced_by_code`, then `parent_code`, to its first-level Area (at most three steps in CLDR).
5. Exactly one distinct first-level Area → it. None, or more than one (`Victoria`: `AU-VIC`, `MT-45`; or two Areas of the same country with the same name) → NotFound.

`Area` carries `Code`, `Kind`, `CountryCode`, `NameEN`, `NameJA *string`, `ReferencePoint *Coordinates`, `TimeZone *string` and `RegionCodes []string`. `ListByCountry(country)` returns the country's first-level Areas, its regions and its time zones, and `ListCountries()` the countries that have first-level Areas with their CLDR territory names, for the organizer's 国 select. The admin approval queue reaches `Resolve` through `rpc.admin.area.v1.AreaService.Resolve` (`usecase/area/resolve`), so a name the admin types (`California`) yields its country before the zone is chosen. `geo.NormalizeAdminArea`, `entity.PrefectureCode` and the Go centroid table are deleted. Diacritic folding (`Cordoba` for `Córdoba`) is not applied: it would make a guess look like an exact match; such a name reaches the admin (Decision 7).

### 4. Where each path gets its area and time zone, and how they are checked

| path | area | time zone | when either does not resolve |
|---|---|---|---|
| discovery (`CreateFromDiscovered`) | Gemini's `admin_area`, resolved in the searcher | the Area's zone, else Gemini's `time_zone` if it is one of the country's zones | staged as a ConcertCandidate, no venue lookup |
| admin approval (`Approve`) | the admin's text, else the candidate's area | the admin's choice, else as discovery | InvalidArgument |
| organizer (`SeriesUseCase.Create` / `Update`) | `EventDraft.admin_area`, the member's selection | `EventDraft.time_zone`, the member's selection | InvalidArgument |
| Home (`SetHome`, onboarding `Create`) | the fan's level 1, Resolve with the code unchanged | — | InvalidArgument |
| reference area (`ListByLocation`) | the caller's area, Resolve with the code unchanged | — | InvalidArgument |

`Venue.Create` validates that the admin area resolves to the same first-level code and that the time zone is one of the Area's country's zones, before the insert; the database backs both up (Decision 5). The Gemini response schema keeps asking for the first-level ISO code (searcher.go:1067) and adds `time_zone`. No path stores a lower-level code converted silently, except discovery and approval, whose sources are text from outside and are recorded on the ConcertCandidate as discovered.

### 5. A Venue has its own time zone

`venues` gains `time_zone TEXT` and a generated `country_code TEXT GENERATED ALWAYS AS (left(admin_area, 2)) STORED`, with `FOREIGN KEY (country_code, time_zone) REFERENCES country_time_zones`; both columns become NOT NULL with `admin_area` (Decision 16). When the Venue's Area has a zone, the Venue's zone equals it (`US-CA` cannot carry `America/New_York`); `Venue.Create` checks it, since a foreign key cannot compare with the Area's zone without a second generated column. The zone belongs to the Venue, not to each Event: a performance's wall-clock time is read at its place, as Ticketmaster's Discovery API also carries a venue's time zone. `entity.VenueTimeZone()` becomes `Venue.Location() *time.Location`, which loads the stored zone from the binary's embedded `time/tzdata`.

### 6. Organizer: the member confirms the name, country, area and time zone of a new place

After a pick, the editor calls `rpc.organizer.venue.v1.VenueService.ResolvePlace(place_id)`. A domain verb, not `Get`: the place may be no Venue yet, and a Venue without an id would break `entity.v1.Venue`'s required id (`venue.proto:12`). The usecase returns the stored Venue when one holds the place id; otherwise it calls `GetPlace` (field mask adds `timeZone`) and returns a `PlaceDraft`: the place's name, its country, the area its address suggests (`administrative_area_level_1`, long name then short name, resolved with the address's `country` short name; for a territory that is its own first-level Area, such as `HK`, the territory itself) and a time zone (the suggested Area's zone, else the place's `timeZone` when it is one of the country's zones). The response is `oneof result { entity.v1.Venue venue; PlaceDraft draft; }`.

```
会場: [ Gocheok Sky Dome          ]
国:   [ 韓国 v ]   地域: [ ソウル特別市 v ]   タイムゾーン: [ ソウル (UTC+9) v ]
------------------------------------------------------------------------------
3月14日(日)  開場 [17:30]  開演 [18:30]  ソウル時間 (日本時間 18:30)
```

For a draft, the editor fills 会場名, 国, 地域 and タイムゾーン; the member may edit each. The 国 select lists `rpc.organizer.area.v1.AreaService.ListCountries`, and changes the 地域 list and the タイムゾーン list, both from `rpc.organizer.area.v1.AreaService.ListByCountry(country_code)`; the 地域 list is grouped by region (`Area.region_codes`), and choosing an Area with a zone selects that zone. The タイムゾーン field is always shown; it is a select when the country has more than one zone and read-only text when it has one. A place already a Venue shows its name, area and zone as text. Every date row shows, after its times, the name of its venue's zone, and, when that zone is not Asia/Tokyo, the start time in Japan time, so a member announcing a show abroad to fans in Japan sees both. On save, `EventDraft.venue_name`, `admin_area` and `time_zone` carry what the member saved; `SeriesUseCase.Create` and `Update` create a new place's Venue with them and the place's coordinates with their fetch time (Decision 9), and never store the draft's values unsaved.

Legal basis: this design assumes that a name, area and time zone prefilled from Places, edited or confirmed by the member and then saved, may be stored (owner's decision of 2026-11-24, without a release gate). The Places policy's exception for an address the end user selects covers street addresses for the user's own transaction, not POI names (developers.google.com/maps/documentation/places/web-service/policies); see Risks for the fallback. Alternatives: no prefill (kept as the fallback); keep storing the derived values (rejected: ToS §3.2.3(a)(iii) and (c)).

### 7. Admin approval queue

`rpc.admin.concert_candidate.v1.ConcertCandidate` gains `admin_area` (`entity.v1.AdminArea`, as discovered), `time_zone` (as resolved by discovery, optional) and `resolved_place_id`, and loses the resolved name and coordinates. The row shows the area by code (地域不明 when absent), the zone (タイムゾーン不明 when absent) and the resolved place as a Google Maps link built from the place id. Every row has an area input, required when the area is absent, and a time zone select of the area's country's zones, required when the zone is absent; `ApproveRequest` gains `admin_area` (`entity.v1.AreaQuery`, a wrapper of a 1-to-100-character code or name, per the wrapper rule of CLAUDE.md "Review criteria") and `time_zone`, resolved in the usecase, so an area present but unresolvable (`JP-99`) is corrected the same way. The zone select lists the zones of the country of the entered area, which the screen learns by resolving the entered text with `rpc.admin.area.v1.AreaService.Resolve` (the candidate's discovered area until the admin enters one), and reads `rpc.admin.area.v1.AreaService.ListByCountry` for that country, served by the same `AreaUseCase.ListByCountry` as the organizer's.

### 8. A Home is a row owned by its User

```sql
CREATE TABLE user_home_areas (
  user_id UUID PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
  area_code TEXT NOT NULL,
  area_first_level BOOLEAN NOT NULL DEFAULT TRUE CHECK (area_first_level),
  FOREIGN KEY (area_code, area_first_level) REFERENCES areas (code, is_first_level)
);
```

The primary key on `user_id` keeps one Home per User; allowing several later changes the key to `(user_id, area_code)` and adds an order column, with no new table and no data migration. Deleting a User deletes its Home. The country code and the reference point are read from `areas` in the same query. `entity.Home` loses `ID`, `Level2` and its stored centroid; `pb` fills `entity.v1.Home.country_code` and `level_1` only. `users.home_id` and `homes` are dropped after the code that no longer reads them is in production. Alternatives: two columns on `users` (rejected: a second Home would need a table and a data migration then); keep `homes` with a foreign key (rejected: an id for a value one User owns, and the orphan problem stays).

### 9. Google place data is a cache

`venues` keeps `google_place_id` (exempt from the caching restrictions) and gains `coordinates_fetch_time TIMESTAMPTZ`, with `CHECK ((latitude IS NULL) = (coordinates_fetch_time IS NULL))`. Every path that takes coordinates from Places writes them with the fetch time. A new CronJob `venue-coordinates-refresh` (backend `cmd/job/venue-coordinates-refresh`, daily at 04:00 Asia/Tokyo, in the backend namespace like `artist-refresh`):

1. Lists the Venues with a place id whose coordinates are missing or were fetched more than 20 days ago, oldest first, at most 1,000 per run.
2. Reads each place's coordinates with `Venue.GetPlaceCoordinates` (Place Details with the field mask `id,location`; `GetPlace`, which also asks for `timeZone`, bills as Pro and is used only on an organizer's pick) and stores the coordinates with the new fetch time; a place that no longer exists clears the coordinates.
3. Clears every coordinate fetched more than 30 days ago, whatever step 2 achieved.

A failed run alerts as the other backend CronJobs do. The 10-day margin lets about nine failed runs pass before any coordinate is lost; a lost coordinate only turns NEARBY into AWAY until the next successful run (`entity/proximity` "Concert with no location").

A Venue's name is never taken from Google: discovery and approval name a new Venue by its listed venue name, the organizer path by the name the member saved. Discovery still reads Google's names to select the right place (`SelectVenuePlace`), during the request only. `concert_candidates` drops `resolved_venue_name`, `resolved_latitude`, `resolved_longitude` and the never-set `resolved_admin_area`, and `rejected_concerts` drops `resolved_venue_name` and `resolved_admin_area`, both keeping `resolved_place_id`; both gain `time_zone` (the zone discovery resolved, optional); approval fetches the coordinates by place id. A Venue's time zone is not refreshed: it was confirmed by a member, the admin or the Area. Alternatives: a geocoder whose results may be stored (rejected: its input would be an address, which Google's terms also forbid storing, and its coverage of Japanese live houses is unknown); no coordinates (rejected: NEARBY needs them).

### 10. The server resolves reference points

`rpc.concert.v1.ListByLocationRequest` replaces `entity.v1.GeoLocation location = 1` (reserved) with `oneof reference { entity.v1.AdminArea admin_area = 4; }`; a point from the device can be added to the oneof later without breaking callers. The usecase resolves the area and uses its reference point; an Area without one returns only HOME concerts. `entity.v1.GeoLocation`, the frontend's `JP_PREFECTURE_CENTROIDS` and `geoLocationFromLevel1` are deleted; the fan Concerts view sends the area code it already holds. `entity.v1.Home.centroid` is reserved.

### 11. The location search at any latitude

The candidate box keeps ±1.8° of latitude and sizes its longitude margin from the reference latitude: `2.0° / cos(min(|lat| + 1.8°, 85°))`, which holds 200 km at every latitude the box reaches, and is the whole longitude range above 85°. A box that crosses ±180° is queried as two longitude ranges. The precise Haversine cut after the box is unchanged.

### 12. Future wall-clock times are stored as wall-clock times

A time that people announce as a wall-clock time at a place, and that lies in the future when stored, is stored as that wall-clock time with its zone; the instant is computed when a rule needs it. This follows iCalendar, which keeps a future event as a local time with a TZID (RFC 5545 §3.2.19, §3.3.5), and the argument in "Storing UTC is not a silver bullet" (Jon Skeet, 2019): a stored instant silently moves away from the announced time when the zone's rules change before the date. A moment in the past (a find time, a scan, a login, a payment) stays an instant.

| record | stored | zone |
|---|---|---|
| Event | `local_event_date DATE` (unchanged), `local_start_time TIME`, `local_open_time TIME` | its Venue's `time_zone` |
| TicketSale | `time_zone TEXT NOT NULL REFERENCES time_zones`, `local_start_time TIMESTAMP`, `local_end_time TIMESTAMP` (without time zone) | the sale's own |
| ConcertCandidate, RejectedConcert | `local_start_time TIME`, `local_open_time TIME` | the candidate's `time_zone` |

`events.start_time`, `open_time` and the sales' `start_time`, `end_time` (`TIMESTAMPTZ`) are replaced. The natural key `uq_events_natural_key` becomes `(venue_id, local_event_date, local_start_time)`: "the same performance" is the same venue, date and announced start, which is what the wall-clock key says. A TicketSale has its own zone because it may offer events of a Series at venues in different zones; an Organizer's sale's zone is one of its events' venues' zones, checked by `TicketSaleUseCase.Create` and `SetWindow`; the editor defaults to the zone they share and asks the member to choose only when they differ (Decision 14); a discovered sale takes the zone the page states (Decision 15). Lengths that rules count in days (an Organizer's Lottery window of 1 to 14 days) are measured on the local date-times, so a window across a daylight-saving change still counts its calendar days.

Computing instants. Go is the authority for every rule: `Event.StartInstant()` and `TicketSale.StartInstant()` build the instant with the zone from the binary's embedded `time/tzdata`. A wall-clock time that does not exist in the zone (a spring-forward gap) is rejected with InvalidArgument when a member enters it and dropped to unknown, with a log line, when discovery finds it; a time that occurs twice (fall-back) is the earlier instant, chosen explicitly rather than left to `time.Date`. SQL filters that need an instant per row use `(local_event_date + local_start_time) AT TIME ZONE v.time_zone` or `local_start_time AT TIME ZONE time_zone`, widened by one day where Go then applies the exact rule, so the rare window in which PostgreSQL's zone data and Go's disagree after a rule change cannot drop a row. No index covers these expressions (`AT TIME ZONE` is not immutable); at hundreds of Events and sales the scans are cheap, and an index on `local_event_date` still narrows them.

Alternatives: keep instants and recompute them on every tzdata release (rejected: the announced wall-clock time is the fact, and the instant would need its own history to know what to recompute); store both (rejected: two values that can disagree).

### 13. Every Event rule uses its Venue's time zone

The current date at a Venue is the date in the Venue's zone (`entity/venue` "Current date at a venue"); every operation that compares an Event's local date with "today" uses it per row: `ListUpcomingByArtist`, `Concert.Search`'s past-date filter, the upcoming and followed lists, the concert page's "ended" state, deletion blockers, and the organizer draft check of `SeriesUseCase.Create` (which compared with the UTC day). `ConcertService.ListFollowed` without `from` returns concerts on or after the current date at each concert's Venue, and the fan Timetable stops sending the device's date for its default view, so a show in London is not dropped while it is still the same day there. An event whose zone is not yet known (a discovered event before its Venue is resolved) is past only when its local date is before the current date in every zone (UTC−12), so it is never dropped early. The admission window (`entity/scanner`) and the resale listing's close time (`entity/resale-listing`) already name the Venue's zone and now get a real one. The daily resale draw runs at 12:00 in the event's Venue's zone (`entity/resale-entry`), which the draw workflow, running every minute, finds by computing each event's next draw instant; Settlement eligibility reads the start instant from Decision 12.

### 14. Times are shown in the zone they belong to

| time | fan web app | organizer console |
|---|---|---|
| an Event's date, open and start, its resale draws and deadline | the Venue's local time; when the viewer's browser zone has another offset at that moment, the zone's name and the viewer's own time in parentheses (`19:00 台北時間（日本時間 20:00）`) | the Venue's local time with the zone's name; Japan time in parentheses when the zone is not Asia/Tokyo |
| a sale's start and end | the viewer's browser zone, with the zone's name when it differs from the sale's zone | the sale's zone, with its name |
| a moment in the past (a scan, a passkey's creation) | the viewer's browser zone | the event's Venue's zone, with its name |
| a server-rendered link preview | the Venue's local time with the zone's name | — |

A sale is a moment a fan acts at wherever the fan is, so it follows the viewer; a performance is attended at its place, so it follows the Venue, as Luma and other event platforms do for in-person events. The organizer console's rule "every date and time in Japan time marked JST" is replaced by the table; its old reason, a member abroad entering JST, holds because every input names its zone. Both apps format through `Intl.DateTimeFormat` with the IANA name from the response. Zone display names of a Venue or a sale come from the API (`time_zones.name_ja` / `name_en`); the viewer's own zone is not known to the API, so its name on fan screens is the browser's localized zone name, the one value a screen shows that no RPC field carries. Adding an Event to the fan's calendar uses the Venue's zone. The organizer guide's "日本時間（JST）" text (`organizer/guide/guide.html`) is rewritten to the same rule. The `Asia/Tokyo` constants in the fan app (`EVENT_TIME_ZONE` and the 14 other files) are removed. Notification texts are unchanged (`entity/notification` already uses the fan's zone).

The organizer's sale editor shows the sale's zone as text when its events' venues share one zone (the usual case) and as a select of their zones only when they differ; its inputs take wall-clock times in that zone.

### 15. Discovery reads wall-clock times and zones

The Gemini searcher asks for each event's local start and open time as `HH:MM` as the page states them, instead of RFC 3339 with an offset, and for each sale's local start and end with the IANA zone the page implies. An event's time zone is its Venue's (Decision 4); a sale whose zone Gemini omits takes the zone its series' venues share, and is otherwise not stored and logged. `entity/ticket-sale/search-published-sales` returns local date-times and a zone ("opens 1 November 12:00 Asia/Taipei", not "13:00 Japan time"), and `upsert-discovered` matches a known sale by its start date in the sale's zone.

### 16. Completing the existing data

1. Migration A (with Decision 1's seed): `UPDATE venues SET admin_area = <first-level>` for the 9 lower-level codes and `FR-75` (15 Venues), and `admin_area = NULL` for any Venue whose code still has no first-level row (`CN-TW` or another omitted code; the migration task counts them read-only before merging), so step 2 finds its area again; a `homes` row with such a code is not copied to `user_home_areas` and its fan picks a Home again; then the composite foreign key `fk_venues_admin_area` (NULL still allowed); `time_zone` set from the Area's zone for every Venue whose Area has one; `name = listed_venue_name` for every Venue with a place id and a listed name; the dropped and added candidate and rejected-concert columns of Decision 9; `coordinates_fetch_time` set to 25 days before the migration on every Venue that has coordinates, in the same statement that adds the column and before its check, so the check holds for existing rows, the first refresh run (which reads coordinates older than 20 days) fetches every Venue's coordinates again, and any it cannot refresh expire 5 days later. The collision check of 2026-11-11 found no pair that would break `idx_venues_listed_name_admin_area`; the migration task repeats it read-only before merging.
2. A one-off subcommand `backfill-venue-areas` of the `concert-discovery` job image, run once as a Kubernetes Job in production with that job's own Gemini credentials: for each Venue without an area or a time zone, it sends the listed venue name and the source page of one of its Events to Gemini, asks for the first-level ISO code and the IANA zone, validates both and writes a CSV (`venue_id, listed_venue_name, answer_area, resolved_code, answer_zone, valid_zone`) to its log. It uses no Google Maps content and writes nothing to the database.
3. The owner reviews the CSV and fills the rows Gemini could not resolve. For each of the 5 listed names held by two Venues, the owner compares the two Venues' place ids, coordinates and Events and records whether they are one venue; only those confirmed as one are merged, and the rest keep both Venues. A row whose Venue is no place a fan can go to (a private event, a show on a cruise ship; Decision 18) the owner marks `NONE` in its `resolved_code` column. For each such row migration B deletes, in this order: the ConcertCandidates of the Venue's listed venue name with no area; the Venue's Events, as `Concert.Delete` does (an Event takes its performers, Concert and TicketJourneys with it); then the discovered Series left with no Event and no ConcertCandidate (the rule of `Series.DeleteOrphaned`, judged after the first two steps) and the Venue. RejectedConcerts stay, since that log is never changed or removed (`entity/rejected-concert`) and it holds no foreign key to a Venue. Before merging, a read-only query checks that none of those Events has a TicketStock, Order, Ticket, Settlement or Scanner, and that none of those Series has a TicketSale, TicketSaleReminder or TicketSaleSearch; a row that has any of them is not deleted and goes back to the owner. The reviewed CSV becomes migration B.
4. Migration C: `admin_area`, `time_zone` and `country_code` NOT NULL, after a read-only check that no NULL is left.
5. Migration D (with the time release): `local_start_time = date_trunc('minute', start_time AT TIME ZONE v.time_zone)::time` and the same for `open_time` on every Event (none has seconds in production, 2026-11-26); each TicketSale gets `time_zone` = the zone its events' venues share (Asia/Tokyo for every Organizer sale today) or, for a discovered sale, the zone its series' venues share, else Asia/Tokyo, and `local_start_time`/`local_end_time` = the instants in that zone cut to the minute (4 of the 8 sales in production, discovered ones stored at the moment they were found, have seconds and milliseconds, which the entity rule refuses; the cut moves each by less than a minute); candidates and rejected concerts likewise. Before merging, a read-only query lists every Organizer Event at a Venue outside Asia/Tokyo (expected none: such an Event's instant was entered as Japan time and needs the owner's correction, not a conversion) and every discovered sale whose series' venues span zones. The old columns are dropped by migration E after the time release has run in production.

### 17. Proto

Two proto PRs, each before the backend and frontend work that needs it (README step 3):

Release 1 (areas, venues, place data):

- `entity.v1.Home`: `reserved 3, 4; reserved "level_2", "centroid";`; `level_1`'s pattern becomes `^[A-Z]{2}(-[A-Z0-9]{1,3})?$` (a territory such as `HK` is a valid Home) and its comment names a first-level Area.
- `entity.v1.GeoLocation`: deleted. `ListByLocationRequest`: `reserved 1; reserved "location";` and a required `oneof reference { entity.v1.AdminArea admin_area = 4; }`.
- `entity.v1.AdminArea`: pattern `^[A-Z]{2}(-[A-Z0-9]{1,3})?$` (a territory without subdivisions, `HK`, is valid); comments say first-level Area.
- `entity.v1.Venue.time_zone` (`entity.v1.TimeZone`, a wrapper of an IANA name).
- New `entity.v1.Area` (`code`, `kind`, `country_code`, `name_en`, optional `name_ja`, repeated `region_codes`, optional `time_zone`), `entity.v1.TimeZoneOption` (`time_zone`, `name_en`, optional `name_ja`) and `entity.v1.AreaQuery`; `rpc.organizer.area.v1.AreaService.ListByCountry` and `ListCountries`, `rpc.admin.area.v1.AreaService.ListByCountry` and `Resolve` (areas, regions, zones, countries); `rpc.organizer.venue.v1.VenueService.ResolvePlace` with `PlaceDraft` (`VenueName name`, `country_code`, optional `AdminArea suggested_admin_area`, optional `TimeZone time_zone`); `EventDraft.admin_area` and `time_zone`; admin `ConcertCandidate.admin_area`, `time_zone`, `resolved_place_id` (without the resolved name and coordinates); `ApproveRequest.admin_area` and `time_zone`.

Release 2 (times):

- `entity.v1.StartTime` and `entity.v1.OpenTime` wrap `google.type.TimeOfDay` instead of `google.protobuf.Timestamp`; an Event is read as `local_date` + these + its Venue's `time_zone`.
- A TicketSale's `start_time` and `end_time` become `google.type.DateTime` with `time_zone` set (the standard type for a civil date-time in a zone), in the entity and in the organizer `Create`/`SetWindow` and fan responses.
- The same for ConcertCandidate's times.
- `ListFollowedRequest.from`'s comment: omitted means each concert's Venue's current date; callers no longer send the device's date for the default view.

Names stay `admin_area` and `level_1` (decided with the user): renaming would break the frontend and the recorded wire contract for a vocabulary gain only.

### Decision 18: a show with no place a fan can go to is not stored

A discovered show listed as `PRIVATE`, or held on a cruise ship, has no public place, no fixed first-level Area and no time zone. It cannot become a Venue, because an Event needs one (`events.venue_id` is NOT NULL) and its wall-clock time is read in the Venue's zone.

Rejected: letting `admin_area` and `time_zone` stay NULL for such a Venue (it would undo migration C and leave the times of release 2 without a zone), and a new kind of Venue (a concept with no value for a fan). Instead the case joins the one discovery already has for a venue that is not announced: "private" and "private event" normalize to an empty venue name, and the searcher's instruction leaves private events and shows on a ship or at sea out. The three Events already stored from such listings are deleted with their Venues in migration B (Decision 16, step 3), after a read-only check that nothing restricts the delete.

### Decision 19: a venue lookup picks only places inside the event's area

The place search words its query with the area code, but the catalog does not restrict its results to it, and the selection took the first place with the listed name wherever it was. Prod (2026-11-26, 887 venues with coordinates) held venues pointing at places in another country, often Japan (a San Francisco venue at Osaka coordinates). The search now returns each place's country and first-level Area (the address components belong to the Text Search Pro SKU the search already pays for, [Text Search field mask](https://developers.google.com/maps/documentation/places/web-service/text-search)), and `Venue.SelectPlace` keeps only places inside the event's admin area; when none is, a place in that country whose region the catalog spells in a way no Area resolves to counts instead, so a venue with such an address is still found. With no such place the event is staged for review, as an unresolved venue is. Rejected: a location restriction rectangle per area (the search takes only a rectangle, which a country or a state does not match), and restricting by country alone (same-named venues exist in several Japanese prefectures).

## Risks / Trade-offs

- [Counsel later finds the prefill of Decision 6 not allowed] → The editor stops prefilling: 会場名 starts with the member's search text, 地域 and タイムゾーン with the Area's zone or no selection. Only the screen scenarios of the prefill change; stored Venues stay, since members saved their values.
- [A country changes its zone rules before an Event] → The stored wall-clock time is right by construction; the computed instant follows the new rules once Go (`time/tzdata`) and Cloud SQL are upgraded. The weekly release check (Decision 2) opens an issue for each tzdata release, and the upgrade of Go is the action.
- [PostgreSQL's and Go's zone data disagree for a while] → SQL filters are widened by a day and Go applies every exact rule (Decision 12).
- [A sale's events span zones] → The member chooses the zone; fans see the sale in their own zone anyway, so the choice only affects how members read it.
- [Place Details pricing] → `id,location` is assumed to bill as Place Details Essentials (10,000 free calls a month against about 1,350 here), and `timeZone` on an organizer's pick as Pro; the refresh task checks the SKU on the first production run.
- [Venue names become the listed names] → Some names carry a source's spelling (`Zepp Haneda(TOKYO)`). The admin and organizer screens can correct a name.
- [Gemini proposes a wrong area or zone for an old Venue] → Nothing is applied without the owner's review of the CSV; a wrong area is worse than none (2026-02-22 D2).
- [A later CLDR or tzdata release reorganizes a country or removes a zone] → The generator, or a composite foreign key, fails until the upgrading change remaps the affected rows (Decision 2).
- [Resolve by name misses spellings without diacritics (`Cordoba`)] → The event is staged and the admin types the code.
- [A generated column cannot be the target of a composite foreign key in the Atlas schema] → The first migration task proves it; the fallback is the eligible-code table of Decision 1's alternatives.
- [Old clients] → Release 1 and release 2 each break one request or response shape (ListByLocation, then times); the frontend is released the same day as each backend release, accepted while the product has no users beyond the owner and one tester.

## Migration Plan

1. Proto release 1, BSR generation.
2. Backend release 1: Migration A, `user_home_areas` backfilled from `homes`, Resolve and the paths of Decision 4, Venue time zones on create, `ResolvePlace`, `ListByCountry`, ListByLocation by area, the new candidate box. Read-only check after deploy: AtlasMigration status, rollout, and a query that every non-NULL `venues.admin_area` and every `user_home_areas.area_code` is a first-level code and every non-NULL `venues.time_zone` is a zone of the Venue's country.
3. cloud-provisioning: the `venue-coordinates-refresh` CronJob; after its first run, a read-only query that every Venue with a place id has coordinates fetched in the last day, except places Google no longer has.
4. Frontend release 1 (same day): organizer venue confirmation with name, country, area and zone; admin area and zone inputs and map link; ListByLocation by area; `JP_PREFECTURE_CENTROIDS` and `level2` removed.
5. Backfill Job, owner review, Migration B, Migration C.
6. Proto release 2, BSR generation.
7. Backend release 2: Migration D, wall-clock times everywhere (Decisions 12, 13, 15). Read-only check: every Event's local times equal its old instants in its Venue's zone, and every sale's window equals its old instants in its zone.
8. Frontend release 2 (same day): time display (Decision 14) in both apps, organizer time and sale inputs in the venue's and sale's zones, `Asia/Tokyo` constants removed.
9. Backend release 3: migration E drops the old time columns, `users.home_id` and `homes`.

Rollback: each release rolls back by image. Migrations A to D are not undone: the old code accepts first-level codes, reads names as text, and ignores the added columns; the old time columns stay until step 9, so a rollback of release 2 reads them, losing only times entered between release 2 and the rollback. `homes` survives until step 9.

## Scenarios verified by hand

Whether the search model leaves a show out depends on its judgement of a live page, so a unit test can only check that the instruction asks for it (`searcher_test.go` asserts the instruction text). The behaviour is read from the discovery results.

@spec-manual components/entity/concert/search "Private event left out" -- the searcher's instruction excludes private events; a show listed as PRIVATE that still gets through is skipped by the venue name normalization (`venue_normalize_test.go`, "Venue not yet announced is missing"); the next discovery run's candidates are read for any.
@spec-manual components/entity/concert/search "Show on a cruise ship left out" -- the searcher's instruction excludes shows on a ship or at sea; the next discovery run's candidates and new Venues are read for a ship.
