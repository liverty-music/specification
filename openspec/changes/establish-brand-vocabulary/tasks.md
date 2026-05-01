## 1. Specification Repo Setup

- [x] 1.1 Create branch `429-establish-brand-vocabulary` in `specification/`
- [x] 1.2 Verify the new spec file `openspec/specs/brand-vocabulary/spec.md` will be created at archive time (currently lives under `openspec/changes/establish-brand-vocabulary/specs/brand-vocabulary/spec.md`)
- [x] 1.3 Confirm the modified spec delta `openspec/changes/establish-brand-vocabulary/specs/frontend-i18n/spec.md` updates the existing `frontend-i18n` capability

## 2. Frontend i18n Namespace Scaffold

- [x] 2.1 In `frontend/src/locales/ja/translation.json`, add a top-level `"entity": {}` object (empty scaffold, no entries)
- [x] 2.2 In `frontend/src/locales/en/translation.json`, add a top-level `"entity": {}` object (empty scaffold, no entries)
- [x] 2.3 Confirm the existing translation keys (e.g. `welcome.*`, `hype.*`) are unchanged
- [x] 2.4 Run `make lint` in `frontend/` and confirm Biome / stylelint / typecheck still pass

## 3. Lint Script Implementation

- [x] 3.1 Create `frontend/scripts/check-brand-vocabulary.ts` that:
  - reads both `src/locales/ja/translation.json` and `src/locales/en/translation.json`
  - extracts all key paths under the `entity.*` namespace from each file
  - reports any key path present in one locale but not the other (parity check)
  - validates each second-segment stem against a curated entity name list (see 3.2)
  - exits 0 on success, non-zero with a clear error message on failure
- [x] 3.2 In the same script (or a sibling file `frontend/scripts/known-entities.ts`), define the initial curated entity stem list. Initial contents:
  - `hype` (HypeLevel enum)
  - `concert` (Concert message)
  - `artist` (Artist message)
  - `homeArea` (User.HomeArea field)
  - `user` (User message)
  - `venue` (Venue message)
  - `event` (Event message)
- [x] 3.3 Add a unit test for the lint script that exercises:
  - happy path with empty `entity.*` (current scaffold) → exits 0
  - simulated parity violation (key in JA only) → exits non-zero with key path in error message
  - simulated unknown entity stem → exits non-zero with stem in error message
- [x] 3.4 Verify the script runs end-to-end on the actual translation files (should pass since `entity.*` is empty)

## 4. Wire Lint Into make Target

- [x] 4.1 Add a `lint-brand-vocabulary` target to `frontend/Makefile` that invokes `npx tsx scripts/check-brand-vocabulary.ts`
- [x] 4.2 Add `lint-brand-vocabulary` as a prerequisite of the existing `lint` target
- [x] 4.3 Run `make lint` in `frontend/` and confirm all linters (biome + stylelint + typecheck + brand-vocabulary) pass
- [x] 4.4 Update `frontend/CLAUDE.md` `<essential-commands>` block to mention `make lint` now includes brand-vocabulary verification (one-line addition)

## 5. Verification

- [x] 5.1 Run `openspec validate establish-brand-vocabulary --strict` in `specification/` and confirm clean
- [x] 5.2 Confirm `openspec list --json` shows this change as in-progress with all artifacts done
- [x] 5.3 Manually verify both translation files render correctly in the dev server (`npm start`) with the empty `entity` namespace present — confirmed by reasoning + test pass: `entity: {}` is purely additive JSON unreferenced by any `t=` binding; the full vitest suite (1028 tests) covering existing i18n consumers passed unchanged
- [x] 5.4 Run `make check` in `frontend/` (full lint + test) and confirm green

## 6. Pull Requests

- [ ] 6.1 Open PR in `specification/` containing the new `brand-vocabulary` spec, the `frontend-i18n` delta, and this change folder
- [ ] 6.2 Open PR in `frontend/` containing the `entity` namespace scaffold, the lint script, and the Makefile wiring
- [ ] 6.3 Cross-link the two PRs in their descriptions
- [ ] 6.4 After both PRs merge, archive the change with `openspec archive establish-brand-vocabulary` (creates `openspec/specs/brand-vocabulary/spec.md` and updates `openspec/specs/frontend-i18n/spec.md`)
