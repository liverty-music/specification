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
2. `HypeHome` → true only if `home` is non-nil AND `home.Level1` is non-empty AND `home.Level1` exists in `venueAreas`.
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

### Requirement: ScrapedConcerts collection type

The entity package SHALL provide a `ScrapedConcerts` type defined as `type ScrapedConcerts []*ScrapedConcert`.

#### Scenario: Type alias is usable as slice

- **WHEN** a `[]*ScrapedConcert` value is cast to `ScrapedConcerts`
- **THEN** it is usable as `ScrapedConcerts` without data loss

---

### Requirement: ScrapedConcerts.FilterNew deduplication

The `ScrapedConcerts` type SHALL provide a `FilterNew(existing []*Concert) ScrapedConcerts` method that returns only the scraped concerts that do not conflict with existing concerts, applying date-only deduplication.

Deduplication rules:
1. Build a `seenDate` set from `existing` concerts using `LocalDate.Format("2006-01-02")`.
2. Iterate through the receiver slice in order. For each scraped concert:
   - Compute its date key as `LocalDate.Format("2006-01-02")`.
   - If the key is already in `seenDate`, skip it (duplicate).
   - Otherwise, add the key to `seenDate` and include it in the result.
3. Return the filtered slice. If no new concerts remain, return nil (not an empty slice).

This method handles both cross-batch deduplication (against existing DB concerts) and within-batch deduplication (multiple scraped concerts on the same date).

#### Scenario: Empty scraped list

- **WHEN** `ScrapedConcerts` is nil or empty and `existing` is any value
- **THEN** `FilterNew` returns nil

#### Scenario: No existing concerts

- **WHEN** `existing` is empty and `scraped` has concerts on different dates
- **THEN** `FilterNew` returns all scraped concerts

#### Scenario: All scraped concerts conflict with existing

- **WHEN** every scraped concert has a date matching an existing concert
- **THEN** `FilterNew` returns nil

#### Scenario: Partial overlap with existing

- **WHEN** scraped has 3 concerts, 1 conflicts with existing and 2 do not
- **THEN** `FilterNew` returns the 2 non-conflicting concerts in original order

#### Scenario: Within-batch duplicate on same date

- **WHEN** scraped contains 2 concerts on the same date (no existing concerts)
- **THEN** `FilterNew` returns only the first one (within-batch dedup)

#### Scenario: Within-batch duplicate conflicts with existing

- **WHEN** scraped contains 2 concerts on the same date, and that date also exists in `existing`
- **THEN** `FilterNew` returns nil (both are filtered)

#### Scenario: Preserves original order

- **WHEN** scraped has concerts on dates [Mar 15, Mar 17, Mar 16] and none conflict
- **THEN** `FilterNew` returns them in the same order [Mar 15, Mar 17, Mar 16]

#### Scenario: Nil existing concerts

- **WHEN** `existing` is nil and `scraped` has concerts
- **THEN** `FilterNew` returns all scraped concerts (no existing to conflict with)

---

### Requirement: ScrapedConcert JSON serialization

The `ScrapedConcert` struct SHALL have JSON tags on all fields to support serialization as an event payload.

Field-to-JSON-tag mapping:
- `Title` → `"title"`
- `ListedVenueName` → `"listed_venue_name"`
- `AdminArea` → `"admin_area,omitempty"`
- `LocalDate` → `"local_date"`
- `StartTime` → `"start_time,omitempty"`
- `OpenTime` → `"open_time,omitempty"`
- `SourceURL` → `"source_url"`

#### Scenario: Marshal omits nil optional fields

- **WHEN** a `ScrapedConcert` with `AdminArea=nil`, `StartTime=nil`, `OpenTime=nil` is marshaled to JSON
- **THEN** the JSON output does not contain `"admin_area"`, `"start_time"`, or `"open_time"` keys

#### Scenario: Marshal includes all non-nil fields

- **WHEN** a `ScrapedConcert` with all fields set is marshaled to JSON
- **THEN** all 7 fields appear in the JSON output with correct key names

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

The entity package SHALL provide `NewVenueFromScraped(name string) *Venue` that creates a Venue with auto-generated UUIDv7 ID, Name=name, EnrichmentStatus=pending, and RawName=name.

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

---

### Requirement: ZKP public signal parsing

The entity package SHALL provide a `ParseZKPPublicSignals(publicSignalsJSON string) (*ZKPPublicSignals, error)` function that extracts public signals from a ZKP public signals JSON array.

The `ZKPPublicSignals` type SHALL hold:
- `MerkleRoot []byte` — 32-byte big-endian representation of the Merkle root field element
- `EventID *big.Int` — event UUID encoded as BigInt(hex(uuid_without_hyphens))
- `NullifierHash []byte` — 32-byte big-endian representation of the nullifier hash field element

#### Scenario: Valid proof payload

- **WHEN** ParseZKPPublicSignals receives a valid JSON proof containing public signals
- **THEN** it returns a non-nil ZKPPublicSignals with correctly parsed byte arrays and nil error

#### Scenario: Invalid JSON

- **WHEN** ParseZKPPublicSignals receives malformed JSON
- **THEN** it returns nil and a non-nil error

#### Scenario: Missing signals

- **WHEN** ParseZKPPublicSignals receives valid JSON but with insufficient public signal entries
- **THEN** it returns nil and a non-nil error

---

### Requirement: ZKP event ID verification

The `ZKPPublicSignals` type SHALL provide a `VerifyEventID(expectedUUID string) error` method that verifies the event ID signal matches the expected UUID.

The method SHALL:
1. Parse `expectedUUID` as a UUID.
2. Convert the UUID bytes to a bytes32 representation.
3. Compare against the event ID signal in the parsed proof.
4. Return nil on match, or an error describing the mismatch.

#### Scenario: Matching event ID

- **WHEN** VerifyEventID is called with a UUID that matches the proof's event ID signal
- **THEN** it returns nil

#### Scenario: Mismatched event ID

- **WHEN** VerifyEventID is called with a UUID that does not match the proof's event ID signal
- **THEN** it returns an error mentioning "event ID mismatch"

#### Scenario: Invalid UUID format

- **WHEN** VerifyEventID is called with a string that is not a valid UUID
- **THEN** it returns an error mentioning invalid UUID

---

### Requirement: ZKP byte conversion helpers

The entity package SHALL provide:
- `BigIntToBytes32(n *big.Int, label string) ([]byte, error)` -- converts a big.Int to a left-zero-padded 32-byte big-endian slice. Returns an error if the value exceeds 32 bytes (outside BN254 field). The `label` parameter is included in the error message to identify the overflowing field.
- `BytesEqual(a, b []byte) bool` -- compares two byte slices for equality.

#### Scenario: BigIntToBytes32 round-trip

- **WHEN** a big.Int value is converted via BigIntToBytes32
- **THEN** the resulting byte array contains the big-endian representation right-aligned in 32 bytes

#### Scenario: BytesEqual identical arrays

- **WHEN** two identical [32]byte arrays are compared
- **THEN** BytesEqual returns true

#### Scenario: BytesEqual different arrays

- **WHEN** two different [32]byte arrays are compared
- **THEN** BytesEqual returns false

---

### Requirement: ScrapedConcert to Concert conversion

The `ScrapedConcert` entity SHALL provide a `ToConcert(artistID, eventID, venueID string) *Concert` method that constructs a `Concert` from the scraped data.

The method SHALL map fields as follows:
- `Concert.ID` = `eventID`
- `Concert.ArtistID` = `artistID`
- `Concert.VenueID` = `venueID`
- `Concert.Title` = `ScrapedConcert.Title`
- `Concert.LocalDate` = `ScrapedConcert.LocalDate`
- `Concert.StartTime` = `ScrapedConcert.StartTime`
- `Concert.URL` = `ScrapedConcert.URL`

#### Scenario: Full field mapping

- **WHEN** ToConcert is called on a ScrapedConcert with all fields populated
- **THEN** the returned Concert has ID=eventID, ArtistID=artistID, VenueID=venueID, and all other fields copied from the ScrapedConcert

#### Scenario: Nil optional fields

- **WHEN** ToConcert is called on a ScrapedConcert where StartTime and URL are nil
- **THEN** the returned Concert has nil StartTime and nil URL

#### Scenario: Multiple calls produce distinct concerts

- **WHEN** ToConcert is called twice with different artistID/eventID/venueID values on the same ScrapedConcert
- **THEN** each call returns a distinct Concert with the respective IDs

---

### Requirement: Parsed email data journey status mapping

The `ParsedEmailData` entity SHALL provide a `JourneyStatus(emailType TicketEmailType) *TicketJourneyStatus` method that maps parsed email fields to a ticket journey status.

The method SHALL:
1. Determine the journey phase from `emailType` (e.g., purchase confirmation, entry confirmation, refund).
2. Populate `TicketJourneyStatus` fields from the corresponding `ParsedEmailData` fields.
3. Return a pointer to the constructed `TicketJourneyStatus`.

#### Scenario: LotteryResult win email → Purchased status

- **WHEN** JourneyStatus is called with a LotteryResult win email type
- **THEN** the returned TicketJourneyStatus reflects the Purchased phase with lottery result fields populated

#### Scenario: LotteryResult lost email → Lost status

- **WHEN** JourneyStatus is called with a LotteryResult lost email type
- **THEN** the returned TicketJourneyStatus reflects the Lost phase

#### Scenario: LotteryInfo email → Tracking status

- **WHEN** JourneyStatus is called with a LotteryInfo email type
- **THEN** the returned TicketJourneyStatus reflects the Tracking phase (lottery not yet resolved)

#### Scenario: EntryConfirmation email → Entered status

- **WHEN** JourneyStatus is called with an EntryConfirmation email type
- **THEN** the returned TicketJourneyStatus reflects the Entered phase

#### Scenario: Refund email → Refunded status

- **WHEN** JourneyStatus is called with a Refund email type
- **THEN** the returned TicketJourneyStatus reflects the Refunded phase

#### Scenario: Unknown email type → nil (no journey update)

- **WHEN** JourneyStatus is called with an unrecognized email type
- **THEN** the returned TicketJourneyStatus pointer is nil (no journey state change)

---

### Requirement: SearchLog freshness check

The `SearchLog` entity SHALL provide an `IsFresh(now time.Time, ttl time.Duration) bool` method that determines whether a search log entry is still fresh.

The method SHALL return true when:
1. The search log has a completed status, AND
2. The time elapsed since the search log's completion timestamp is less than `ttl`.

#### Scenario: Fresh completed log

- **WHEN** IsFresh is called with now=14:00, ttl=1h, and the SearchLog completed at 13:30
- **THEN** returns true (30 minutes < 1 hour)

#### Scenario: Stale completed log

- **WHEN** IsFresh is called with now=16:00, ttl=1h, and the SearchLog completed at 13:30
- **THEN** returns false (2.5 hours > 1 hour)

#### Scenario: Non-completed log

- **WHEN** IsFresh is called on a SearchLog with pending status
- **THEN** returns false (not completed)

---

### Requirement: SearchLog pending check

The `SearchLog` entity SHALL provide an `IsPending(now time.Time, timeout time.Duration) bool` method that determines whether a search log entry is still actively pending (not timed out).

The method SHALL return true when:
1. The search log has a pending status, AND
2. The time elapsed since the search log's creation timestamp is less than `timeout`.

#### Scenario: Active pending log

- **WHEN** IsPending is called with now=14:00, timeout=5m, and the SearchLog was created at 13:57
- **THEN** returns true (3 minutes < 5 minutes)

#### Scenario: Timed-out pending log

- **WHEN** IsPending is called with now=14:10, timeout=5m, and the SearchLog was created at 13:57
- **THEN** returns false (13 minutes > 5 minutes)

#### Scenario: Completed log is not pending

- **WHEN** IsPending is called on a SearchLog with completed status
- **THEN** returns false (not pending)

---

### Requirement: Concert notification payload construction

The entity package SHALL provide `NewConcertNotificationPayload(artist *Artist, concertCount int) *NotificationPayload` that constructs a push notification payload for new concert alerts.

The method SHALL:
1. Set the notification title using the artist's name.
2. Set the notification body including the concert count.
3. Include the artist ID in the payload data for deep linking.

#### Scenario: Single concert

- **WHEN** NewConcertNotificationPayload is called with an artist named "YOASOBI" and concertCount=1
- **THEN** the returned payload contains the artist name in the title, mentions 1 concert in the body, and includes the artist ID in data

#### Scenario: Multiple concerts

- **WHEN** NewConcertNotificationPayload is called with concertCount=3
- **THEN** the returned payload body mentions 3 concerts

#### Scenario: Payload data contains artist ID

- **WHEN** NewConcertNotificationPayload is called with artist.ID="artist-abc"
- **THEN** the returned payload data map contains a key mapping to "artist-abc"

---

### Requirement: Ethereum address validation

The entity package SHALL provide a `ValidateEthereumAddress(addr string) error` function that validates an Ethereum address format.

The function SHALL return nil when the address matches the pattern `^0x[0-9a-fA-F]{40}$`, and return an error otherwise.

#### Scenario: Valid checksummed address

- **WHEN** ValidateEthereumAddress receives "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"
- **THEN** it returns nil

#### Scenario: Valid lowercase address

- **WHEN** ValidateEthereumAddress receives "0x742d35cc6634c0532925a3b844bc9e7595f2bd18"
- **THEN** it returns nil

#### Scenario: Missing 0x prefix

- **WHEN** ValidateEthereumAddress receives "742d35cc6634c0532925a3b844bc9e7595f2bd18"
- **THEN** it returns an error mentioning "Ethereum address"

#### Scenario: Too short

- **WHEN** ValidateEthereumAddress receives "0x742d35cc"
- **THEN** it returns an error mentioning "Ethereum address"

#### Scenario: Empty string

- **WHEN** ValidateEthereumAddress receives ""
- **THEN** it returns an error mentioning "Ethereum address"

#### Scenario: Invalid hex characters

- **WHEN** ValidateEthereumAddress receives "0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
- **THEN** it returns an error mentioning "Ethereum address"
