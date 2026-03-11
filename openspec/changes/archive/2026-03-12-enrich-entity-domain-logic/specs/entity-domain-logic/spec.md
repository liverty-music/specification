## ADDED Requirements

### Requirement: Home validation

The `Home` entity SHALL provide a `Validate() error` method that enforces structural integrity of geographic home area data. The method SHALL return the first validation error encountered.

Validation rules:
1. `CountryCode` MUST match ISO 3166-1 alpha-2 format (`^[A-Z]{2}$`).
2. `Level1` MUST match ISO 3166-2 subdivision format (`^[A-Z]{2}-[A-Z0-9]{1,3}$`).
3. The first two characters of `Level1` MUST equal `CountryCode`.
4. When `Level2` is non-nil, its length MUST be between 1 and 20 characters inclusive.

#### Scenario: Valid home with all fields

- **WHEN** Home has CountryCode="JP", Level1="JP-13", Level2=nil
- **THEN** Validate returns nil

#### Scenario: Valid home with Level2

- **WHEN** Home has CountryCode="JP", Level1="JP-13", Level2="Shibuya"
- **THEN** Validate returns nil

#### Scenario: Invalid country code format

- **WHEN** Home has CountryCode="j" (lowercase or wrong length)
- **THEN** Validate returns error mentioning "ISO 3166-1 alpha-2"

#### Scenario: Invalid Level1 format

- **WHEN** Home has Level1="INVALID"
- **THEN** Validate returns error mentioning "ISO 3166-2"

#### Scenario: Level1 prefix mismatch

- **WHEN** Home has CountryCode="JP" but Level1="US-CA"
- **THEN** Validate returns error mentioning prefix mismatch

#### Scenario: Level2 empty string

- **WHEN** Home has Level2 pointing to an empty string
- **THEN** Validate returns error mentioning "1 and 20 characters"

#### Scenario: Level2 too long

- **WHEN** Home has Level2 pointing to a 21-character string
- **THEN** Validate returns error mentioning "1 and 20 characters"

---

### Requirement: Hype validity check

The `Hype` type SHALL provide an `IsValid() bool` method that returns true only for the four defined values: `watch`, `home`, `nearby`, `away`.

#### Scenario: Known hype values

- **WHEN** Hype is one of HypeWatch, HypeHome, HypeNearby, HypeAway
- **THEN** IsValid returns true

#### Scenario: Unknown hype value

- **WHEN** Hype is "unknown" or an empty string
- **THEN** IsValid returns false

---

### Requirement: Hype-based notification eligibility

The `Hype` type SHALL provide a `ShouldNotify(home *Home, venueAreas map[string]struct{}, concerts []*Concert) bool` method that determines whether a follower with this hype level should receive push notifications for a batch of new concerts.

Decision rules (evaluated in order):
1. `HypeWatch` → false (never notify).
2. `HypeHome` → true only if `home` is non-nil AND `home.Level1` exists in `venueAreas`.
3. `HypeNearby` → true only if any concert has `ProximityHome` or `ProximityNearby` relative to `home`.
4. `HypeAway` → true (always notify).
5. Any other value → false.

#### Scenario: HypeWatch never notifies

- **WHEN** Hype is HypeWatch with any home and concerts
- **THEN** ShouldNotify returns false

#### Scenario: HypeHome matches venue area

- **WHEN** Hype is HypeHome, home.Level1="JP-13", venueAreas contains "JP-13"
- **THEN** ShouldNotify returns true

#### Scenario: HypeHome no match

- **WHEN** Hype is HypeHome, home.Level1="JP-13", venueAreas contains only "JP-27"
- **THEN** ShouldNotify returns false

#### Scenario: HypeHome with nil home

- **WHEN** Hype is HypeHome, home is nil
- **THEN** ShouldNotify returns false

#### Scenario: HypeHome with empty Level1

- **WHEN** Hype is HypeHome, home.Level1 is empty string
- **THEN** ShouldNotify returns false

#### Scenario: HypeNearby with nearby concert

- **WHEN** Hype is HypeNearby, home has centroid, a concert venue is within 200km
- **THEN** ShouldNotify returns true

#### Scenario: HypeNearby with only distant concerts

- **WHEN** Hype is HypeNearby, all concerts are beyond 200km
- **THEN** ShouldNotify returns false

#### Scenario: HypeNearby with nil home

- **WHEN** Hype is HypeNearby, home is nil
- **THEN** ShouldNotify returns false

#### Scenario: HypeAway always notifies

- **WHEN** Hype is HypeAway with any home and concerts
- **THEN** ShouldNotify returns true

#### Scenario: Unknown hype skips

- **WHEN** Hype is "unknown"
- **THEN** ShouldNotify returns false

---

### Requirement: Concert proximity grouping

The entity package SHALL provide a `GroupByDateAndProximity(concerts []*Concert, home *Home) []*ProximityGroup` function that classifies concerts into Home/Nearby/Distant buckets grouped by calendar date.

Rules:
1. Concerts SHALL be grouped by `LocalDate` formatted as "YYYY-MM-DD".
2. Within each group, each concert SHALL be classified using `Concert.ProximityTo(home)`.
3. Groups SHALL be returned in the order of first appearance (preserving input date order).
4. An empty or nil input SHALL return nil.

#### Scenario: Empty input

- **WHEN** concerts slice is empty
- **THEN** function returns nil

#### Scenario: Single date, mixed proximity

- **WHEN** three concerts on 2026-03-15: one HOME, one NEARBY, one AWAY
- **THEN** returns one ProximityGroup with correct bucket assignments

#### Scenario: Multiple dates preserve order

- **WHEN** concerts span March 15, March 17, March 16 (in that input order)
- **THEN** returns three groups in order: March 15, March 17, March 16

#### Scenario: Nil home classifies all as Distant

- **WHEN** home is nil, concerts have venues
- **THEN** all concerts are placed in the Distant bucket

---

### Requirement: Concert proximity classification

The existing `Concert.ProximityTo(home *Home) Proximity` method SHALL classify a concert's geographic proximity to the user's home area.

Classification rules (evaluated in order):
1. AWAY — if `home` is nil or `Venue` is nil.
2. HOME — if venue's `AdminArea` matches `home.Level1`.
3. NEARBY — if venue has `Coordinates`, home has `Centroid`, and Haversine distance ≤ 200km.
4. AWAY — everything else.

#### Scenario: Nil home

- **WHEN** home is nil
- **THEN** returns ProximityAway

#### Scenario: Nil venue

- **WHEN** concert has no venue
- **THEN** returns ProximityAway

#### Scenario: Admin area match

- **WHEN** venue.AdminArea="JP-13" and home.Level1="JP-13"
- **THEN** returns ProximityHome

#### Scenario: Admin area mismatch with nearby coordinates

- **WHEN** venue.AdminArea="JP-14" (Kanagawa), home.Level1="JP-13" (Tokyo), venue is 30km from home centroid
- **THEN** returns ProximityNearby

#### Scenario: Admin area mismatch beyond threshold

- **WHEN** venue is 500km from home centroid, admin areas differ
- **THEN** returns ProximityAway

#### Scenario: Venue has no coordinates

- **WHEN** venue.Coordinates is nil, admin areas differ
- **THEN** returns ProximityAway

#### Scenario: Home has no centroid

- **WHEN** home.Centroid is nil, admin areas differ
- **THEN** returns ProximityAway

#### Scenario: Admin area match takes priority over distance

- **WHEN** venue.AdminArea matches home.Level1, even though distance > 200km
- **THEN** returns ProximityHome (admin area check runs first)

#### Scenario: Venue admin area is nil

- **WHEN** venue.AdminArea is nil, venue has coordinates within 200km of home
- **THEN** returns ProximityNearby

---

### Requirement: Scraped concert deduplication key

The `ScrapedConcert` entity SHALL provide a `DedupeKey() string` method that generates a unique deduplication key from its natural key fields.

Key format: `"YYYY-MM-DD|<listed_venue_name>"` when `StartTime` is nil, or `"YYYY-MM-DD|<listed_venue_name>|HH:MM:SSZ"` when `StartTime` is non-nil (UTC formatted).

#### Scenario: Without start time

- **WHEN** ScrapedConcert has LocalDate=2026-03-15, ListedVenueName="Zepp Tokyo", StartTime=nil
- **THEN** DedupeKey returns "2026-03-15|Zepp Tokyo"

#### Scenario: With start time

- **WHEN** ScrapedConcert has LocalDate=2026-03-15, ListedVenueName="Zepp Tokyo", StartTime=19:00 UTC
- **THEN** DedupeKey returns "2026-03-15|Zepp Tokyo|19:00:00Z"

#### Scenario: DateVenueKey subset

- **WHEN** ScrapedConcert has a start time
- **THEN** DedupeKey begins with DateVenueKey value

---

### Requirement: Artist filtering by MBID

The entity package SHALL provide a `FilterArtistsByMBID(artists []*Artist) []*Artist` function that removes artists with empty MBID and deduplicates by MBID keeping the first occurrence.

#### Scenario: Mixed valid and empty MBIDs

- **WHEN** input contains artists with MBIDs ["abc", "", "def", "abc"]
- **THEN** returns artists with MBIDs ["abc", "def"] in order

#### Scenario: All empty MBIDs

- **WHEN** all artists have empty MBID
- **THEN** returns empty slice

#### Scenario: No duplicates

- **WHEN** all artists have unique non-empty MBIDs
- **THEN** returns all artists unchanged

#### Scenario: Empty input

- **WHEN** input is nil or empty
- **THEN** returns empty slice

---

### Requirement: OfficialSite constructor

The entity package SHALL provide `NewOfficialSite(artistID, url string) *OfficialSite` that creates an OfficialSite with an auto-generated UUIDv7 ID.

#### Scenario: Constructor generates ID

- **WHEN** NewOfficialSite("artist-123", "https://example.com") is called
- **THEN** returned OfficialSite has non-empty ID, ArtistID="artist-123", URL="https://example.com"

#### Scenario: ID is unique per call

- **WHEN** NewOfficialSite is called twice with the same arguments
- **THEN** each call returns a different ID

---

### Requirement: Venue constructor from scraped data

The entity package SHALL provide `NewVenueFromScraped(name string) *Venue` that creates a Venue with auto-generated UUIDv7 ID, EnrichmentStatus=pending, and RawName=name.

#### Scenario: Constructor sets defaults

- **WHEN** NewVenueFromScraped("Zepp Tokyo") is called
- **THEN** returned Venue has non-empty ID, Name="Zepp Tokyo", RawName="Zepp Tokyo", EnrichmentStatus=EnrichmentStatusPending

---

### Requirement: Token ID generation

The entity package SHALL provide `GenerateTokenID() (uint64, error)` that produces an ERC-721 token ID from the high 64 bits of a UUIDv7.

#### Scenario: Generates non-zero token ID

- **WHEN** GenerateTokenID is called
- **THEN** returns a non-zero uint64 and nil error

#### Scenario: Monotonically increasing

- **WHEN** GenerateTokenID is called twice in sequence
- **THEN** second value is greater than or equal to first (UUIDv7 timestamp ordering)
