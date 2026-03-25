## ADDED Requirements

### Requirement: ZKP public signal parsing

The entity package SHALL provide a `ParseZKPPublicSignals(proof []byte) (*ZKPPublicSignals, error)` function that extracts public signals from a ZKP proof JSON payload.

The `ZKPPublicSignals` type SHALL hold the parsed signal values as `[32]byte` arrays.

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
- `BigIntToBytes32(b *big.Int) [32]byte` -- converts a big.Int to a right-padded 32-byte array.
- `BytesEqual(a, b [32]byte) bool` -- compares two 32-byte arrays for equality.

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

#### Scenario: Purchase confirmation email

- **WHEN** JourneyStatus is called with a purchase confirmation email type
- **THEN** the returned TicketJourneyStatus reflects the purchased phase with relevant parsed fields

#### Scenario: Entry confirmation email

- **WHEN** JourneyStatus is called with an entry confirmation email type
- **THEN** the returned TicketJourneyStatus reflects the entered phase

#### Scenario: Refund email

- **WHEN** JourneyStatus is called with a refund email type
- **THEN** the returned TicketJourneyStatus reflects the refunded phase

#### Scenario: Unknown email type

- **WHEN** JourneyStatus is called with an unrecognized email type
- **THEN** the returned TicketJourneyStatus has a default/unknown phase

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

## MODIFIED Requirements

(No modifications to existing requirements. All changes are additive.)
