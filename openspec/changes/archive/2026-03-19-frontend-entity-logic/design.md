## Context

The frontend `entities/` layer was introduced to centralize type definitions mirroring the Go backend's `entity` package. Currently, `artist.ts` is the only entity file with pure functions (`bestLogoUrl`, `bestBackgroundUrl`); the rest are type-only. Business logic lives in framework-coupled services, routes, and state reducers, making it untestable without Aurelia DI or store setup.

The Go backend's `internal/entity/` contains rich domain logic (hype notification eligibility, proximity classification, concert grouping, validation). The frontend should follow the same pattern for its domain rules.

Current adapter layer structure:
```
src/adapter/
  rpc/client/    ← UseCase → proto (outbound)
  rpc/mapper/    ← proto → Entity (inbound)
  storage/       ← Entity ↔ localStorage
```

Presentation-derived pure logic (artist color hashing, hype display metadata) is scattered across components and routes with no consistent home.

## Goals / Non-Goals

**Goals:**
- Extract pure business logic from services/state/routes/components into `entities/` as framework-free, independently testable pure functions
- Establish `adapter/view/` as the canonical location for entity-to-view-model transformations shared across multiple components
- Achieve architectural consistency with the Go backend's entity layer pattern
- Enable unit testing of domain rules without Aurelia DI, store, or DOM dependencies

**Non-Goals:**
- Refactoring the adapter/rpc layer (mapper and client structure stays as-is)
- Moving single-component-specific presentation logic (e.g., `getStageParams` stays in `dna-orb/`)
- Creating entity classes with methods (stay with interfaces + pure functions to match existing pattern)
- Changing any runtime behavior — this is a structural refactor only

## Decisions

### 1. Pure functions alongside interfaces (not classes)

The existing `artist.ts` pattern uses `export interface Artist` + `export function bestLogoUrl(artist)`. All entity files will follow this same pattern: interfaces for data shape, exported pure functions for business logic.

**Alternative considered**: Entity classes with methods (e.g., `concert.isHypeMatched(lane)`). Rejected because the codebase already uses plain objects from proto mappers, and wrapping them in class instances would add unnecessary construction overhead and change the data flow pattern.

### 2. `adapter/view/` for shared presentation logic

Presentation-derived pure functions that are referenced by 2+ components go in `adapter/view/`. This follows Clean Architecture's Interface Adapters layer — `adapter/` already contains `rpc/` (inbound) and `storage/` (persistence), so `view/` (outbound to UI) is the natural extension.

**Alternative considered**: Top-level `presentation/` directory. Rejected because the adapter layer already has precedent for non-RPC adapters (`adapter/storage/`), and `adapter/view/` maintains consistency with Clean Architecture's layer model where the Go backend also places its mappers in `adapter/`.

**Boundary rule**: If a pure function is only used by one component, it stays colocated with that component. It moves to `adapter/view/` only when shared.

### 3. Entity file organization: one file per domain concept

Each entity file owns the types AND logic for its domain concept:
- `concert.ts` — Concert interface + `isHypeMatched()` + hype/lane ordering constants
- `follow.ts` — FollowedArtist/Hype types + `hasFollow()` dedup check
- `user.ts` — User/UserHome types + `codeToHome()` + `displayName()`
- `entry.ts` — MerklePath type + `bytesToDecimal()` + `uuidToFieldElement()`
- `onboarding.ts` (new) — OnboardingStep enum + STEP_ORDER + `stepIndex()` + predicates

**Alternative considered**: Separate `entities/concert-rules.ts` for logic vs `entities/concert.ts` for types. Rejected as over-separation — the Go backend keeps both in the same file (e.g., `concert.go` has both struct and methods).

### 4. Location logic stays with User entity

`codeToHome()`, `displayName()`, and the prefecture data currently in `constants/iso3166.ts` are domain knowledge about the `UserHome` entity. They move to `entities/user.ts` (or a new `entities/location.ts` if the file grows too large).

`constants/iso3166.ts` will remain as the data source (prefecture records, region groups, quick-select cities) since these are reference data, not business logic. Only the pure functions (`codeToHome`, `displayName`, `translationKey`) move.

### 5. Reducer delegates to entity functions

The Redux reducer (`state/reducer.ts`) currently implements duplicate-follow prevention inline. After extraction, it will call `hasFollow(state.guest.follows, artistId)` from `entities/follow.ts`. The reducer remains the state mutation point, but the business rule lives in the entity.

Same pattern for `middleware.ts` step migration: delegates to `normalizeStep()` from `entities/onboarding.ts`.

## Risks / Trade-offs

**[Circular import risk]** Entity files must not import from services, state, or components. Since entities are the innermost layer, this is enforced by convention. → Mitigation: Biome lint rule or ESLint `import/no-restricted-paths` can enforce this boundary if needed.

**[Moving `iso3166.ts` functions]** Components that currently import from `constants/iso3166.ts` will need import path updates. → Mitigation: Re-export from `constants/iso3166.ts` during transition, remove re-exports in a follow-up.

**[Test file placement]** Entity tests should live alongside entity files (e.g., `entities/concert.spec.ts`). This is a new pattern for the frontend — current tests are in `__tests__/` or colocated with components. → Mitigation: Follow the colocated pattern already used in the project; Vitest supports any `*.spec.ts` location.
