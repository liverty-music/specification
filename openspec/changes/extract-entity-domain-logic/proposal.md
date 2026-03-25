## Why

The first round of entity-layer enrichment (enrich-entity-domain-logic) moved validation, classification, grouping, and constructor logic into `entity/`. However, several other pieces of pure business logic remain trapped in the usecase layer: ZKP signal parsing, concert construction from scraped data, ticket email journey mapping, search log freshness checks, and push notification payload building. These functions depend only on entity fields and have no usecase-layer dependencies (no repositories, no external services). Keeping them in usecase forces callers to mock orchestration infrastructure just to test deterministic transformations. Extracting them improves testability, discoverability, and domain cohesion.

## What Changes

- **Move ZKP signal parsing to entity layer**: Relocate `parsePublicSignals`, `bigIntToBytes32`, `bytesEqual`, and `publicSignals` type from `entry_uc.go` to `entity/zkp_signals.go`. Rename `publicSignals` to `ZKPPublicSignals` and export all functions. Add `ZKPPublicSignals.VerifyEventID()` method.
- **Add ScrapedConcert.ToConcert receiver method**: Extract inline Concert construction from `concert_uc.go` and `concert_creation_uc.go` into a single `ScrapedConcert.ToConcert(artistID, eventID, venueID string) *Concert` method on the entity.
- **Add ParsedEmailData.JourneyStatus receiver method**: Move `mapParsedToJourneyStatus` from `ticket_email_uc.go` into `ParsedEmailData.JourneyStatus(emailType TicketEmailType) *TicketJourneyStatus` on the entity.
- **Add SearchLog freshness methods**: Extract inline freshness/pending checks from `concert_uc.go` into `SearchLog.IsFresh(now, ttl)` and `SearchLog.IsPending(now, timeout)` methods.
- **Add push notification payload constructor**: Move payload struct and construction from `push_notification_uc.go` into `entity/push_notification.go` as `NewConcertNotificationPayload(artist, concertCount)`.

## Capabilities

### New Capabilities

(none -- all additions extend the existing `entity-domain-logic` capability)

### Modified Capabilities

- `entity-domain-logic`: Add 5 new groups of entity-layer logic -- ZKP signal parsing, concert construction from scraped data, email journey status mapping, search log freshness checks, and notification payload construction.

## Impact

- **`internal/entity/`**: New file `zkp_signals.go`; new methods on `ScrapedConcert`, `ParsedEmailData`, `SearchLog`; new constructor in `push_notification.go`. Corresponding `_test.go` files added.
- **`internal/usecase/`**: Private functions removed and replaced with entity-layer method calls in `entry_uc.go`, `concert_uc.go`, `concert_creation_uc.go`, `ticket_email_uc.go`, `push_notification_uc.go`.
- **No API changes**: No proto, RPC, or database changes. Purely internal refactoring.
- **No migration needed**: No schema or infrastructure impact.
