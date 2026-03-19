## Why

The `frontend-entity-logic` change extracted pure business logic into `entities/` and `adapter/view/` layers but shipped with minimal happy-path tests. Several functions lack edge-case coverage, one module (`translationKey`) has zero tests, and `adapter/view/hype-display.ts` has no test file at all. Comprehensive tests are needed to lock down the contracts before downstream code builds on them.

## What Changes

- Add missing edge-case and boundary tests for all extracted entity functions (`concert`, `follow`, `onboarding`, `user`, `entry`)
- Add missing function-level coverage for `translationKey()` in `entities/user.ts`
- Add missing test file for `adapter/view/hype-display.ts`
- Strengthen `adapter/view/artist-color.ts` tests with falsy-but-valid boundary cases (`dominantHue === 0`)
- Verify `normalizeStep()` covers all legacy numeric mappings including gap values (`'2'`, `'6'`)

## Capabilities

### New Capabilities

- `entity-test-coverage`: Comprehensive unit test suite for all pure functions in `entities/` and `adapter/view/` layers

### Modified Capabilities

- `frontend-entity-layer`: Test coverage requirement added for all exported pure functions
- `frontend-testing`: Entity and view-adapter test conventions established

## Impact

- Test files: `entities/*.spec.ts`, `adapter/view/*.spec.ts`
- No production code changes
- Increases unit test count and branch coverage for the entity layer
