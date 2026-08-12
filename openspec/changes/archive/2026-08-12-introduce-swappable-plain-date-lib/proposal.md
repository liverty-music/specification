## Why

The frontend's calendar arithmetic — weekend/range preset resolution, `<input type="date">` parse/format, inclusive day spans, `CalendarDate` conversions — is scattered across `date-presets.ts`, `date-preset-selector.ts`, and `concert-store.ts` and built entirely on the native `Date` object. `Date` forces us to hand-guard footguns it creates across all of these: silent month rollover (the `new Date(2026, -1, 15)` → 2025-12-15 pattern that already required an explicit null-guard in `concert-store.ts` to avoid misbucketing a concert), midnight-local normalization to avoid DST drift, and `Date.UTC` hacks for day-span math. TC39 `Temporal` (ES2026, Stage 4 since 2026-03) eliminates this whole class of bugs and its `Temporal.PlainDate` maps 1:1 onto our existing `CalendarDate` value type — but it is **not yet Baseline** (Chrome 144 / Firefox 139 ship it; Safari only in Technology Preview) and its `@js-temporal/polyfill` is ~44 KB gzipped. We ship **zero** date libraries today, so adopting Temporal natively now would be a pure +44 KB bundle regression for a mobile PWA that tracks INP/LCP.

This change builds the seam now — while the analysis is fresh — so that the eventual switch to native `Temporal` is a one-line, already-proven change once it reaches Baseline, without paying any bundle cost in the meantime.

## What Changes

- Introduce a new frontend library `src/lib/plain-date/` that exposes calendar arithmetic through an **implementation-agnostic interface** whose boundary values are always the plain `CalendarDate` data type (no `Date` or `Temporal` object crosses the boundary).
- Move the existing pure calendar primitives (`addDays`, `resolveWeekend`, `parseDateInput`, `formatDateInput`, `inclusiveDaySpan`, and a Date-less `todayCalendarDate` replacing the current `toCalendarDate(d: Date)`) out of `date-presets.ts` into a **`Date`-backed implementation** behind that interface. Call sites import the interface entry point, not a concrete implementation. The All-Nearby glue that is not pure calendar math — `resolvePreset`, `DateRange`, `DatePresetId`, `MAX_RANGE_DAYS`, `rangeCacheKey` — stays in `date-presets.ts` and re-points onto the new primitives.
- Add a **second `Temporal`-backed implementation** of the same interface (referencing `globalThis.Temporal`, never importing the polyfill in application code).
- Add `@js-temporal/polyfill` as a **`devDependencies`-only** package, used solely to run the `Temporal` implementation under Vitest/jsdom (where `globalThis.Temporal` is absent on Node 25).
- Add a **shared differential test suite** run against BOTH implementations that fixes the behavioral contract (including the semantic decision points: invalid-component handling, weekend rules, span clamping) so the two engines are proven equivalent.
- Select the active implementation at **build time via Vite `resolve.alias`** keyed on mode/env (a build-time flag, NOT a runtime flag): production builds resolve to the `Date` implementation only; the `Temporal` implementation is tree-shaken out. This keeps the production bundle at **+0 KB**.
- Add a **CI guard** asserting the production bundle contains no `@js-temporal` / Temporal-polyfill code, so the +0 KB property cannot silently regress.

Out of scope (explicitly deferred): the `Temporal`-ization of relative-time formatting (`toRelative`) and `Intl` display formatting in `value-converters/date.ts` (Instant/Intl concerns, little Temporal upside); and migrating `concert-store.ts`'s own date construction (`concertFrom`, `timestampToTimeString`) and the `Concert.date: Date` UI entity field to the new library / `CalendarDate` (wider UI blast radius — tracked separately). Those keep their existing inline guards for now; this change establishes the reusable seam they will later adopt.

## Capabilities

### New Capabilities

- `frontend-plain-date-lib`: An implementation-agnostic calendar-arithmetic library for the SPA. Defines the `CalendarDate`-boundary interface, its behavioral contract (weekend/range preset resolution, date-input parse/format, inclusive day span, invalid-component handling), the requirement that two interchangeable engines (`Date` and `Temporal`) satisfy that contract identically under a shared test suite, build-time engine selection, and the production-bundle purity guarantee (no Temporal polyfill shipped).

### Modified Capabilities

<!-- None. The observable behavior of the All Nearby date presets (specced in passive-concert-discovery) is intentionally unchanged; this change relocates the implementation behind a seam without altering any user-facing behavior. -->

## Impact

- **New code**: `frontend/src/lib/plain-date/` (interface + `Date` impl + `Temporal` impl + shared differential tests).
- **Modified code**: `frontend/src/components/all-nearby/date-presets.ts` and `date-preset-selector.ts` re-point to the new interface; `date-presets.ts` retains only the `all-nearby`-specific glue (`DateRange`, `DatePresetId`, `MAX_RANGE_DAYS`, `rangeCacheKey`) that is not pure calendar arithmetic.
- **Build config**: `frontend/vite.config.ts` gains a mode-keyed `resolve.alias` for the plain-date engine.
- **Dependencies**: `@js-temporal/polyfill` added to `devDependencies` only.
- **CI**: a new bundle-purity assertion (test or build-step grep) in the frontend pipeline.
- **No backend, proto, or infra impact.** No user-facing behavior change.
