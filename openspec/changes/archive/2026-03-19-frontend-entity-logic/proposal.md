## Why

Business logic in the frontend is scattered across services, routes, and components, making it difficult to unit test without framework dependencies. The Go backend already follows Clean Architecture with a rich `entity` package containing pure domain logic. The frontend `entities/` layer currently holds only type definitions (except `artist.ts`), while business rules like hype matching, onboarding step progression, and follow deduplication live in framework-coupled code. Extracting these into `entities/` and establishing `adapter/view/` for presentation-layer pure logic will align the frontend with the backend's architecture and dramatically improve testability.

## What Changes

- Extract pure business rules from `services/`, `routes/`, `components/`, and `state/` into `entities/` as framework-free pure functions
- Create `adapter/view/` directory for UI-derived pure logic (entity-to-view-model transformations) that is referenced by multiple components
- Move domain constants and predicates (hype ordering, onboarding steps, location code parsing) into their corresponding entity files
- Move binary/crypto conversion utilities into `entities/entry.ts` alongside `MerklePath`
- Relocate `OnboardingStep` enum, step ordering, and predicates from `onboarding-service.ts` into a new `entities/onboarding.ts`
- Keep single-component-specific presentation logic colocated (e.g., `getStageParams` stays in `dna-orb/`)

## Capabilities

### New Capabilities
- `frontend-entity-business-logic`: Pure business logic functions extracted into `entities/` — hype matching, follow deduplication, onboarding step progression, location code parsing, and Merkle path conversions
- `frontend-view-adapter`: `adapter/view/` layer for entity-to-view-model pure functions shared across multiple components — artist color derivation, hype display metadata

### Modified Capabilities
- `frontend-entity-layer`: Entity files gain pure functions alongside existing type definitions, extending the pattern established by `artist.ts` (which already has `bestLogoUrl`, `bestBackgroundUrl`)

## Impact

- **Frontend `entities/`**: `concert.ts`, `follow.ts`, `user.ts`, `entry.ts` gain exported pure functions; new `onboarding.ts` created
- **Frontend `adapter/view/`**: New directory with `artist-color.ts`, `hype-display.ts`
- **Frontend `services/`**: `dashboard-service.ts`, `onboarding-service.ts`, `proof-service.ts` lose inline logic, import from entities instead
- **Frontend `state/`**: `reducer.ts` delegates duplicate-follow check to `follow.ts`; `middleware.ts` delegates step migration to `onboarding.ts`
- **Frontend `components/`**: `color-generator.ts` moves to `adapter/view/artist-color.ts`; `my-artists-route.ts` imports `HYPE_TIERS` from `adapter/view/`
- **No API, proto, or backend changes required**
