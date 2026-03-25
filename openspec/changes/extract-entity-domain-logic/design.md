## Context

The first entity-layer enrichment (`enrich-entity-domain-logic`) established the pattern of moving pure business logic from `usecase/` to `entity/`. That change covered validation, enum methods, proximity classification, grouping, filtering, and constructors. Five additional groups of pure logic remain in the usecase layer. Each depends only on entity fields and has no repository or service dependencies, making them strong candidates for extraction.

The codebase already has precedent for both receiver methods (e.g., `ScrapedConcert.DedupeKey()`, `Concert.ProximityTo()`) and package-level functions (e.g., `FilterArtistsByMBID()`, `GroupByDateAndProximity()`). This change follows the same conventions.

## Goals / Non-Goals

**Goals:**
- Extract 5 groups of pure business logic from usecase to entity layer
- Use receiver methods where the logic is intrinsic to a single entity instance
- Use package-level constructor functions for payload creation that spans multiple entities
- Achieve comprehensive test coverage for all extracted logic
- Maintain identical runtime behavior (pure refactoring)

**Non-Goals:**
- Moving orchestration logic that requires repositories or external services
- Changing any public API, proto schema, or database schema
- Refactoring usecase layer beyond replacing inlined logic with entity method calls
- Introducing new domain concepts or changing existing entity struct fields

## Decisions

### 1. ScrapedConcert.ToConcert as a receiver method

**Decision**: `func (sc *ScrapedConcert) ToConcert(artistID, eventID, venueID string) *Concert` -- a receiver method on `ScrapedConcert`.

**Rationale**: The transformation is intrinsic to the ScrapedConcert entity -- it maps scraped fields to Concert fields. The receiver pattern makes the relationship between source and target explicit. The `eventID` and `venueID` parameters are required because the `concert_creation_uc` code path generates these IDs before conversion (unlike the simpler `concert_uc` path where the Concert gets an auto-generated ID). Using a single method signature with all three parameters unifies both call sites.

**Alternative considered**: Standalone `NewConcertFromScraped()` factory function. Rejected because it obscures which entity drives the transformation and doesn't match the existing `ScrapedConcert.DedupeKey()` method pattern.

### 2. ParsedEmailData.JourneyStatus as a receiver method

**Decision**: `func (p *ParsedEmailData) JourneyStatus(emailType TicketEmailType) *TicketJourneyStatus` -- a receiver method on `ParsedEmailData`.

**Rationale**: The mapping logic reads fields from `ParsedEmailData` to construct a `TicketJourneyStatus`. The receiver pattern makes the data flow clear: parsed email data produces a journey status. The `emailType` parameter is external context required for the mapping but is itself a domain type.

**Alternative considered**: Standalone `mapParsedToJourneyStatus(emailType, parsed)`. Rejected because it loses the OOP cohesion of having the entity know how to transform itself.

### 3. SearchLog freshness as receiver methods

**Decision**: Two methods on `SearchLog`:
- `func (sl *SearchLog) IsFresh(now time.Time, ttl time.Duration) bool`
- `func (sl *SearchLog) IsPending(now time.Time, timeout time.Duration) bool`

**Rationale**: Freshness and pending checks are intrinsic properties of a search log entry. Injecting `now` and `ttl`/`timeout` as parameters keeps the methods pure and testable without clock mocking. This matches the existing pattern where time-dependent logic receives `now` as a parameter.

### 4. ZKP signal parsing as entity types and functions

**Decision**: Create `entity/zkp_signals.go` with:
- `type ZKPPublicSignals` (renamed from private `publicSignals`)
- `func ParseZKPPublicSignals(proof []byte) (*ZKPPublicSignals, error)`
- `func (s *ZKPPublicSignals) VerifyEventID(expectedUUID string) error`
- Helper functions `BigIntToBytes32`, `BytesEqual` exported for reuse

**Rationale**: The signal parsing logic is purely mathematical/cryptographic with no infrastructure dependencies. The `publicSignals` type is a domain concept (zero-knowledge proof signals) that belongs in the entity layer. Exporting the helpers enables testing and potential reuse by other verification flows.

### 5. Push notification payload as a constructor

**Decision**: `func NewConcertNotificationPayload(artist *Artist, concertCount int) *NotificationPayload` as a package-level constructor in `entity/push_notification.go`.

**Rationale**: The payload construction reads from `Artist` and a count, producing a `NotificationPayload`. This follows the existing `NewArtist`, `NewOfficialSite`, `NewVenueFromScraped` constructor pattern. A package-level function is appropriate because it composes data from multiple inputs rather than transforming a single entity.

### 6. Test file organization

**Decision**: Tests follow the existing convention -- one `_test.go` per source file, same package.

| Source | Test file |
|--------|-----------|
| `zkp_signals.go` | `zkp_signals_test.go` |
| `concert.go` | `concert_test.go` (extend) |
| `ticket_email.go` or `ticket_email_parser.go` | corresponding `_test.go` |
| `search_log.go` | `search_log_test.go` |
| `push_notification.go` | `push_notification_test.go` (extend) |

## Risks / Trade-offs

- **[Risk] Usecase tests may break** -- Usecase tests referencing the moved private functions will need updating. Mitigation: replacement is mechanical (call entity method instead of local function).
- **[Risk] ZKP helper export surface** -- Exporting `BigIntToBytes32` and `BytesEqual` increases the entity package's public API. Mitigation: these are stable cryptographic primitives unlikely to change, and keeping them in entity avoids circular imports if other entry-point logic needs them.
- **[Trade-off] ScrapedConcert.ToConcert parameter count** -- Three string parameters (`artistID, eventID, venueID`) could be confused. Mitigation: parameter names are descriptive and match existing field names; the method is called from only two sites.
- **[Trade-off] Entity package grows** -- More code in entity/. Acceptable because it is domain logic that belongs there, offset by reduced usecase complexity and improved testability.
