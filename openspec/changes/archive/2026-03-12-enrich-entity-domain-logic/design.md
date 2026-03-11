## Context

The backend follows Clean Architecture with entity, usecase, adapter, and infrastructure layers. Currently the entity layer (`internal/entity/`) contains mostly pure data structs and interface definitions, with only one business logic method (`Concert.ProximityTo()`). Pure business rules — validation, classification, deduplication, construction — are spread across `internal/usecase/` as private helper functions, making them harder to test and reuse.

The existing `NewArtist` constructor sets the pattern: entity constructors generate UUIDs and set defaults. Several other entities are constructed inline in usecases with ad-hoc UUID generation.

## Goals / Non-Goals

**Goals:**
- Move all pure business logic (functions that depend only on entity fields) from usecase to entity layer
- Add constructor functions for entities that need ID generation or default values
- Add validation methods on domain types
- Achieve comprehensive test coverage for all entity-layer logic (new and existing)

**Non-Goals:**
- Moving orchestration logic that requires repositories or external services
- Changing any public API, proto schema, or database schema
- Refactoring the usecase layer beyond replacing inlined logic with entity method calls
- Moving interfaces between layers (entity/ vs usecase/ interface placement is a separate discussion)

## Decisions

### 1. Methods vs package-level functions

**Decision**: Use receiver methods when the logic is intrinsic to a single entity instance. Use package-level functions when operating on slices or across multiple entity types.

| Function | Style | Rationale |
|----------|-------|-----------|
| `Home.Validate()` | Method | Validates its own fields |
| `Hype.ShouldNotify(home, concerts)` | Method on `Hype` | Hype determines the decision |
| `Hype.IsValid()` | Method | Enum self-validation |
| `ScrapedConcert.DedupeKey()` | Method | Derives key from own fields |
| `GroupByDateAndProximity(concerts, home)` | Package function | Operates on a slice, returns `[]*ProximityGroup` |
| `FilterArtistsByMBID(artists)` | Package function | Slice operation |
| `GenerateTokenID()` | Package function | No receiver, pure generation |
| `NewOfficialSite(artistID, url)` | Package function (constructor) | Follows `NewArtist` pattern |
| `NewVenueFromScraped(name)` | Package function (constructor) | ID + defaults |

**Alternative considered**: Creating type aliases for slices (e.g., `type Concerts []*Concert`) with methods. Rejected — adds indirection without proportional benefit for the current codebase size.

### 2. Error return type for validation

**Decision**: Entity validation methods return `error` (stdlib), not `apperr` types.

**Rationale**: Entity layer should not depend on application error libraries (`apperr`, `codes`). The usecase caller wraps the error with `apperr.New(codes.InvalidArgument, err.Error())` as needed. This keeps the entity layer framework-free.

**Alternative considered**: Return `apperr` directly from entity. Rejected — introduces infrastructure dependency into the domain core.

### 3. `Hype.ShouldNotify` scope

**Decision**: `Hype.ShouldNotify(home *Home, venueAreas map[string]struct{}, concerts []*Concert) bool`

The method receives pre-computed `venueAreas` (a map of venue admin areas from the concert batch) rather than computing it internally. This avoids repeated iteration when checking multiple followers against the same concert batch.

**Rationale**: The usecase already computes `venueAreas` once for the entire follower loop. Passing it in keeps the entity method pure while preserving the optimization.

### 4. Test file organization

**Decision**: One `_test.go` file per entity source file, in the same package (`package entity`).

| Source | Test file |
|--------|-----------|
| `concert.go` | `concert_test.go` |
| `user.go` | `user_test.go` |
| `follow.go` | `follow_test.go` |
| `artist.go` | `artist_test.go` |
| `ticket.go` | `ticket_test.go` |

All tests use table-driven patterns. No mocks needed — these are pure function tests.

## Risks / Trade-offs

- **[Risk] Usecase tests may break** → Usecase tests that call the moved private functions will need updating. Mitigation: the replacement is mechanical (call entity function instead of local one). Usecase tests that test orchestration remain valid.
- **[Risk] Signature changes during move** → Some functions need slight signature adjustments (e.g., `Hype.ShouldNotify` receives `venueAreas` parameter). Mitigation: compile-time verification ensures correctness.
- **[Trade-off] Entity package grows** → More code in entity/. Acceptable because it's domain logic that belongs there, and it's offset by reduced usecase complexity.
