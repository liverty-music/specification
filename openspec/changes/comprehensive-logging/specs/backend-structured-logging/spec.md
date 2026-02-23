## ADDED Requirements

### Requirement: Blockchain Client Logging
The system SHALL log all blockchain RPC operations with structured attributes for operational visibility and troubleshooting.

#### Scenario: Blockchain RPC connection initialization is logged
- **WHEN** the blockchain client establishes an RPC connection
- **THEN** the system SHALL log at INFO level with message indicating connection target
- **AND** the log SHALL include attributes: `component=ticketsbt`, `rpcEndpoint`

#### Scenario: Successful mint transaction is logged
- **WHEN** a mint transaction completes successfully
- **THEN** the system SHALL log at INFO level with message "ticket minted"
- **AND** the log SHALL include attributes: `tokenID`, `userID`, `eventID`, `txHash`

#### Scenario: Mint retry attempts are logged
- **WHEN** a mint transaction fails and is retried
- **THEN** the system SHALL log at DEBUG level for each retry attempt
- **AND** the log SHALL include attributes: `attempt`, `maxAttempts`, `tokenID`, `error`
- **AND** on final failure, the system SHALL log at ERROR level with response body

#### Scenario: On-chain owner query is logged
- **WHEN** the system queries token ownership on-chain
- **THEN** the system SHALL log at DEBUG level with attributes: `tokenID`
- **AND** on failure, the system SHALL log at ERROR level with response body

#### Scenario: Token existence check anomaly is logged
- **WHEN** `IsTokenMinted` encounters an unexpected error (not ERC721NonexistentToken)
- **THEN** the system SHALL log at WARN level with attributes: `tokenID`, `error`

---

### Requirement: External API Client Logging
The system SHALL log all outbound HTTP requests to external APIs with context attributes for troubleshooting.

#### Scenario: Last.fm API request is logged
- **WHEN** the system makes an HTTP request to the Last.fm API (search, getSimilar, getTop)
- **THEN** the system SHALL log at INFO level with message indicating the operation
- **AND** the log SHALL include attributes: `component=lastfm`, `method` (API method), `artistID` or `query` (as applicable)
- **AND** on failure, the system SHALL log at ERROR level with `statusCode`

#### Scenario: MusicBrainz API request is logged
- **WHEN** the system makes an HTTP request to MusicBrainz (getArtist, resolveURL, searchPlace)
- **THEN** the system SHALL log at INFO level with operation and context
- **AND** the log SHALL include attributes: `component=musicbrainz`, `mbid` or `venueName` (as applicable)
- **AND** on URL resolution fallback, the system SHALL log at WARN level indicating which URL was selected

#### Scenario: Google Maps API request is logged
- **WHEN** the system makes an HTTP request to Google Maps Text Search API
- **THEN** the system SHALL log at INFO level with attributes: `component=googlemaps`, `venueName`
- **AND** on failure, the system SHALL log at ERROR level with `statusCode`

#### Scenario: Gemini API request is logged
- **WHEN** the system makes a Vertex AI Gemini grounded search request
- **THEN** the system SHALL log at INFO level with attributes: `component=gemini`, `artistID`, `query`
- **AND** on failure, the system SHALL log at ERROR level
- **AND** on invalid date parsing, the system SHALL log at WARN level

#### Scenario: Rate limiter backoff is logged
- **WHEN** an external API client waits due to rate limiting
- **THEN** the system SHALL log at DEBUG level with attributes: `component`, `backoffMs`

---

### Requirement: Database Mutation Logging
The system SHALL log all database write operations (INSERT, UPDATE) at INFO level with entity context.

#### Scenario: Successful INSERT is logged
- **WHEN** a new record is inserted into the database
- **THEN** the system SHALL log at INFO level with message indicating entity creation
- **AND** the log SHALL include attributes: `entityType` (ticket, user, concert, venue, artist), `entityID`

#### Scenario: Constraint violation on INSERT is logged
- **WHEN** an INSERT fails due to a unique constraint violation (duplicate key)
- **THEN** the system SHALL log at WARN level with message indicating duplicate
- **AND** the log SHALL include attributes: `entityType`, `entityID` or identifying fields

#### Scenario: Successful UPDATE is logged
- **WHEN** a record is updated in the database (e.g., safe address update)
- **THEN** the system SHALL log at INFO level with message indicating entity update
- **AND** the log SHALL include attributes: `entityType`, `entityID`, `field` (updated field name)

---

### Requirement: Entry Verification Step Logging
The system SHALL log each step of the entry verification process at INFO level for audit trail.

#### Scenario: Event ID verification result is logged
- **WHEN** the system verifies that the proof's event ID matches the requested event
- **THEN** the system SHALL log at INFO level with attributes: `step=eventID`, `eventID`, `match` (boolean)

#### Scenario: Merkle root comparison result is logged
- **WHEN** the system compares the proof's Merkle root against the expected root
- **THEN** the system SHALL log at INFO level with attributes: `step=merkleRoot`, `eventID`, `match` (boolean)

#### Scenario: Nullifier duplicate check result is logged
- **WHEN** the system checks whether the nullifier has been used before
- **THEN** the system SHALL log at INFO level with attributes: `step=nullifier`, `eventID`, `userID`, `isDuplicate` (boolean)
- **AND** if the nullifier is a duplicate, the system SHALL log at WARN level with message "duplicate entry attempt"
