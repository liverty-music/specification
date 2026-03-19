## Context

The `frontend-entity-logic` change extracted 13 pure functions and 2 constants across 7 modules into `entities/` and `adapter/view/`. Initial tests covered happy paths but left gaps in edge cases, boundary conditions, and one module (`translationKey`) with zero coverage. Since these functions form the contract layer that services and components depend on, comprehensive tests are essential before further development builds on them.

## Goals / Non-Goals

**Goals:**
- Achieve comprehensive branch coverage for every exported pure function in `entities/` and `adapter/view/`
- Cover all boundary and edge cases identified in the gap analysis
- Add missing test file for `adapter/view/hype-display.ts`
- Add missing `translationKey()` tests in `entities/user.spec.ts`

**Non-Goals:**
- Testing framework-dependent code (services, components, state)
- Changing production code (test-only change)
- Achieving 100% line coverage on interface/type exports

## Decisions

### 1. Co-located spec files

Tests remain co-located with source (`entities/*.spec.ts`, `adapter/view/*.spec.ts`) rather than in the `test/` directory. This matches the pattern established in `frontend-entity-logic` and keeps pure-function tests close to their implementations.

**Alternative considered**: Moving to `test/entities/`. Rejected because co-location makes it easier to verify coverage at a glance and avoids deep relative import paths.

### 2. Table-driven tests for combinatorial coverage

Functions like `isHypeMatched` (4 hypes x 3 lanes = 12 combinations) and `normalizeStep` (all legacy numeric values + gaps) use `it.each` table-driven style to exhaustively cover the input space without verbose duplication.

### 3. Structural assertion for constant completeness

`HYPE_TIERS` and `HYPE_ORDER` / `LANE_ORDER` tests verify that every value of the union type has a corresponding entry. This catches silent breakage when a new enum value is added to the type but not to the constant.

## Risks / Trade-offs

- **Risk**: Tests could become brittle if they assert exact hash values for `artistHue`. → Mitigation: Assert range and determinism properties, not specific numbers.
- **Risk**: `dominantHue === 0` boundary test may surface an actual bug in `artistHueFromColorProfile`. → Mitigation: If the `!= null` check is correct, the test documents that `0` is valid. If not, it exposes the bug early.
