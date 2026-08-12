## 1. Library scaffold & interface

- [ ] 1.1 Create `frontend/src/lib/plain-date/` with `index.ts` re-exporting the fixed contract (`CalendarDate`, `DateRangeCD`, `todayCalendarDate`, `addDays`, `resolveWeekend`, `parseDateInput`, `formatDateInput`, `inclusiveDaySpan`, `isValidCalendarDate`) from a virtual engine specifier (`plain-date-engine`).
- [ ] 1.2 Define the boundary types so no `Date`/`Temporal` object appears in any signature; source `CalendarDate` from the existing RPC client type where possible to avoid a duplicate shape.
- [ ] 1.3 Add a `tsconfig` path mapping (and/or `.d.ts`) for `plain-date-engine` so IDE/type resolution points at the interface regardless of the built engine.

## 2. Date engine (ships to prod)

- [ ] 2.1 Implement `date-impl.ts` by moving the pure calendar functions out of `date-presets.ts` (`addDays`, `resolveWeekend`, `parseDateInput`, `formatDateInput`, `inclusiveDaySpan`), preserving current local-component behavior. Replace the current `toCalendarDate(d: Date)` — whose `Date` parameter would violate the no-`Date`-at-the-boundary requirement — with a Date-less `todayCalendarDate(): CalendarDate` (grep confirms `toCalendarDate` has no external callers, so this is a safe internal rename).
- [ ] 2.2 Implement `isValidCalendarDate` and make `parseDateInput`/interpretation reject out-of-domain components (no silent rollover) — matching the current null-guard behavior in `concert-store.ts` / `date-presets.ts`.

## 3. Temporal engine (built now, shipped later)

- [ ] 3.1 Implement `temporal-impl.ts` against `globalThis.Temporal.PlainDate`; do NOT import the polyfill in this module.
- [ ] 3.2 Map the semantic divergence points to the contract: catch `PlainDate.from` throws on invalid components and return `null`; drop DST normalization (unnecessary with `PlainDate`); match `"YYYY-MM-DD"` formatting.

## 4. Build-time engine selection

- [ ] 4.1 Add `@js-temporal/polyfill` to `frontend/package.json` `devDependencies` only.
- [ ] 4.2 Add a mode-keyed `resolve.alias` in `vite.config.ts` mapping `plain-date-engine` → `date-impl` by default, → `temporal-impl` when `VITE_DATE_ENGINE=temporal`.
- [ ] 4.3 Verify the default build resolves to the Date engine and the Temporal engine module is absent from emitted chunks (and vice-versa under the opt-in).

## 5. Differential test suite

- [ ] 5.1 Add a scoped Vitest setup that installs `@js-temporal/polyfill` on `globalThis` for the differential suite only (no leak into the wider test run).
- [ ] 5.2 Write the parametrized suite importing both engines directly, asserting deep equality across all contract operations, with explicit cases for weekend rules (Mon–Fri / Sat / Sun), inclusive span (equal → 1, +29 → 30), parse/format round-trips, and `month=0` / out-of-domain rejection.

## 6. Migrate call sites

- [ ] 6.1 Repoint `date-presets.ts` and `date-preset-selector.ts` to import the calendar primitives from `src/lib/plain-date`; keep All-Nearby glue (`DateRange`, `DatePresetId`, `MAX_RANGE_DAYS`, `resolvePreset`, `rangeCacheKey`) in `date-presets.ts`.
- [ ] 6.2 Grep `frontend/src` (excluding `src/lib/plain-date/`) to confirm no consumer imports a concrete engine or `@js-temporal/polyfill`.
- [ ] 6.3 Confirm existing All-Nearby preset tests remain green (behavior unchanged).

## 7. CI bundle-purity guard

- [ ] 7.1 Add a check that scans production `dist/` chunks for `@js-temporal` / polyfill identifiers and fails on any hit; assert `@js-temporal/polyfill` is not in `dependencies`.
- [ ] 7.2 Wire the guard into `make check` / the frontend CI pipeline.

## 8. Verify & ship to prod

- [ ] 8.1 Run `make check` (lint + typecheck + tests incl. differential suite) and `npm run build`; confirm the bundle-purity guard passes and bundle size is unchanged vs. baseline.
- [ ] 8.2 Open the frontend PR, pass CI, and merge.
- [ ] 8.3 Cut the frontend GitHub Release (SemVer minor) → automated prod pin-bump → confirm ArgoCD sync so the change reaches prod (Date engine, +0 KB). No behavior change to verify at runtime.
