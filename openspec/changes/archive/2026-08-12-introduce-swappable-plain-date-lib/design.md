## Context

See proposal.md — Why. Today the frontend has no date library and does all civil-date math on native `Date`, scattered across `date-presets.ts`, `date-preset-selector.ts`, and `concert-store.ts`. The domain already carries the right value type: `CalendarDate { year, month, day }` (1-based month/day), defined in the generated RPC client. `Temporal.PlainDate` is a structural match for `CalendarDate`, but Temporal is not yet Baseline (Safari ships it only in Technology Preview as of 2026-08) and `@js-temporal/polyfill` is ~44 KB gzipped — an unacceptable regression for a PWA that ships zero date libraries today.

Relevant environment facts that shape the design:
- Node 25 (the current dev/test runtime) has **no** `globalThis.Temporal`; Vitest runs under jsdom, so the Temporal engine's tests must supply the polyfill themselves.
- `vite.config.ts` already uses `loadEnv` / `VITE_*`, so a mode-keyed `resolve.alias` is a natural fit.
- The `frontend-runtime-config` capability already establishes the precedent of grep/bundle-content CI assertions — the polyfill-purity guard follows the same pattern.

## Goals / Non-Goals

**Goals:**
- One import seam (`src/lib/plain-date`) for all pure civil-date arithmetic, with `CalendarDate`/primitives as the only boundary types.
- Two engines (`Date`, `Temporal`) proven equivalent by a single shared differential test suite.
- Build-time engine selection that tree-shakes the unselected engine; production ships the `Date` engine at +0 KB.
- A CI guard that fails if the Temporal polyfill ever reaches the production bundle.

**Non-Goals:**
- Temporal-izing relative-time (`toRelative`) or `Intl` display formatting in `value-converters/date.ts` (Instant/Intl concerns; deferred).
- Migrating `Concert.date: Date` to `CalendarDate` (wider UI blast radius; deferred to a separate change).
- Any change to the observable behavior of the All Nearby date presets (owned by `passive-concert-discovery`).
- Actually switching production to Temporal — this change only builds the seam; the flip happens later, once Temporal is Baseline.

## Decisions

### D1: Interface as a module of pure functions over `CalendarDate`, not a DI service

The seam is a plain ES module (`src/lib/plain-date/index.ts`) re-exporting a fixed set of pure functions. Proposed contract (names owned here, behavior owned by the spec):

```ts
// Boundary types only — no Date/Temporal ever crosses.
export interface CalendarDate { year: number; month: number; day: number }
export interface DateRangeCD { from: CalendarDate; to: CalendarDate }

export function todayCalendarDate(): CalendarDate               // local components
export function addDays(d: CalendarDate, days: number): CalendarDate
export function resolveWeekend(base: CalendarDate): DateRangeCD
export function parseDateInput(value: string): CalendarDate | null
export function formatDateInput(d: CalendarDate): string        // "YYYY-MM-DD"
export function inclusiveDaySpan(from: CalendarDate, to: CalendarDate): number
export function isValidCalendarDate(d: CalendarDate): boolean
```

- **Why functions over a DI-injected `IPlainDateOps` service?** DI registration keeps both engines reachable at runtime, defeating tree-shaking — the exact opposite of the +0 KB goal. A module seam resolved by the bundler eliminates the dead engine statically. DI would also add observation/injection overhead for what is pure, stateless math.
- **Why `CalendarDate` at the boundary (not `Date`)?** It is the anti-corruption boundary: with only plain data crossing, the two engines are trivially swappable and the differential test needs no adapter. It also stops raw `Date` from leaking further into the UI (the existing `Concert.date: Date` leak is explicitly left alone but not widened).
- `resolvePreset` / `DateRange` / `DatePresetId` / `MAX_RANGE_DAYS` / `rangeCacheKey` stay in `date-presets.ts` — they are All-Nearby glue (preset enum, cache key), not pure calendar math. `date-presets.ts` re-exports the calendar primitives from the new lib so its public surface is unchanged for current importers where practical.

### D2: Engine selection via mode-keyed Vite `resolve.alias` (build-time), not a runtime flag

`index.ts` imports from a virtual specifier (e.g. `plain-date-engine`) that `vite.config.ts` aliases to the concrete engine file based on an env flag:

```ts
// vite.config.ts (sketch)
const engine = env.VITE_DATE_ENGINE === 'temporal' ? 'temporal-impl' : 'date-impl'
resolve: { alias: { 'plain-date-engine': `/src/lib/plain-date/${engine}.ts` } }
```

- **Why alias, not a conditional `import`?** A top-level `import` of both engines with a runtime branch bundles both (and drags in the polyfill if the Temporal engine references it). A `resolve.alias` picks exactly one file at build time; the other is never in the module graph, so it is not merely tree-shaken but never resolved. This is what guarantees +0 KB.
- **Default = `date-impl`.** `temporal` requires the explicit `VITE_DATE_ENGINE=temporal` opt-in, used only for CI equivalence builds / future validation — never the default.

### D3: Temporal engine references `globalThis.Temporal`; polyfill is test-only

- The Temporal engine (`temporal-impl.ts`) uses `globalThis.Temporal.PlainDate` and never imports the polyfill, so a future native build is 0 KB.
- Vitest cannot see `globalThis.Temporal` on Node 25, so the differential test's setup imports `@js-temporal/polyfill` and installs it on `globalThis` for the test run only. `@js-temporal/polyfill` is added to **`devDependencies`**.

### D4: Differential test as the executable contract

A single parametrized Vitest suite imports both `date-impl` and `temporal-impl` directly (bypassing the alias) and runs every contract case against both, asserting deep equality. The one genuine semantic divergence and two convergent-by-construction cases are pinned as explicit contract cases:

| Case | `Date` engine | `Temporal` engine | Contract |
|---|---|---|---|
| Out-of-domain component (e.g. `month=0`) — **the real divergence** | silent rollover | `PlainDate.from` throws | both return `null` at boundary → Temporal engine catches the throw, Date engine validates before constructing |
| Day arithmetic (`addDays`) | pure calendar-day math on a date-only value | pure calendar-day math on `PlainDate` | identical `CalendarDate` out. Because the boundary is `CalendarDate`→`CalendarDate` (no wall-clock time), neither engine is DST-sensitive — the current `resolvePreset` midnight-local normalization is no longer needed by *either* engine and is dropped |
| `formatDateInput` zero-padding | manual `padStart` | `PlainDate.toString()` / `padStart` | identical `"YYYY-MM-DD"` |

The suite doubles as the regression fence for the eventual native-Temporal flip.

### D5: Bundle-purity CI guard

After `npm run build`, a check greps the emitted `dist/` chunks for `@js-temporal` / polyfill identifiers and fails on any hit (mirrors the `frontend-runtime-config` bundle-content assertions). Runs in the default-engine (Date) build. Wired into `make check` / CI so the +0 KB property cannot silently regress.

## Risks / Trade-offs

- **Two implementations to maintain until the flip (~1 year).** → The interface is tiny (7 functions) and frozen by the differential suite; drift is caught by CI. Scope is deliberately limited to pure calendar math to keep the surface minimal.
- **Temporal engine is written now but never exercised in production until Baseline (rot risk).** → The shared differential suite runs the Temporal engine on every CI run via the polyfill, so it stays honest against the same contract as the shipped engine.
- **`resolve.alias` virtual specifier could confuse IDE/type resolution.** → Provide a matching `tsconfig` path mapping (and/or a `.d.ts`) for `plain-date-engine` so types resolve to the interface regardless of the built engine.
- **Polyfill accidentally imported by application code (bundle regression).** → D5's CI guard fails the build; the Temporal engine references `globalThis.Temporal` only, and the spec forbids polyfill imports outside tests.
- **Node/jsdom polyfill install leaks between tests.** → Install on `globalThis` in a scoped setup file used only by the differential suite; do not install globally for the whole test run.

## Migration Plan

1. Land the lib (interface + both engines + differential suite + alias + CI guard) with production defaulting to the `Date` engine — behavior-neutral, ships immediately.
2. Repoint `date-presets.ts` / `date-preset-selector.ts` to the interface; keep All-Nearby glue in place. Existing preset tests stay green (behavior unchanged).
3. **Later, separate change (not this one):** once Temporal is Baseline (Safari stable + widely available), flip the default alias to a native-Temporal build (no polyfill), verify the differential suite + bundle-purity guard, ship. Rollback = revert the one-line alias default.

## Open Questions

- Exact `dist/` scan mechanism for D5 (standalone Vitest test vs. a `make`-level grep step) — either satisfies the spec; pick during implementation.
