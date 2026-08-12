# frontend-plain-date-lib Specification

## Purpose
This capability defines the SPA's implementation-agnostic calendar-arithmetic library: a single seam through which all pure "civil date" math (weekend/range preset resolution, `<input type="date">` parse/format, inclusive day-span, `CalendarDate` conversions) flows. It fixes one behavioral contract that two interchangeable engines — a native `Date` engine (shipped today) and a `Temporal` engine (shipped when Baseline) — SHALL satisfy identically, so the frontend can migrate from `Date` to `Temporal` at build time without any behavior change and without a production bundle-size regression.
## Requirements
### Requirement: Calendar arithmetic SHALL be exposed through an implementation-agnostic interface with `CalendarDate` boundary values

The SPA SHALL provide its pure calendar arithmetic through a single library entry point (`src/lib/plain-date`) that exposes a fixed interface. Every value that crosses the interface boundary — as an argument or a return value — SHALL be either a primitive (`number`, `string`) or the plain `CalendarDate` data type (`{ year: number; month: number; day: number }`, all 1-based for month/day). No engine-specific temporal object (a native `Date` instance or a `Temporal.PlainDate` instance) SHALL appear in any interface signature. Call sites SHALL import the interface entry point and SHALL NOT import a concrete engine implementation directly.

#### Scenario: Boundary exposes only plain data

- **WHEN** any function of the plain-date library entry point is called from application code
- **THEN** its parameters and return value SHALL be primitives or `CalendarDate` objects only
- **AND** no native `Date` or `Temporal` object SHALL be passed across or returned from the boundary

#### Scenario: Call sites depend on the interface, not an engine

- **WHEN** searching `frontend/src` (excluding `src/lib/plain-date/`) for imports of a concrete engine module (e.g. a `*-impl` path or `@js-temporal/polyfill`)
- **THEN** zero occurrences SHALL be found
- **AND** every consumer SHALL import from the `src/lib/plain-date` entry point instead

### Requirement: The library SHALL implement a fixed calendar-arithmetic contract

The library SHALL provide, at minimum, the following operations with the specified behavior, independent of the active engine:

- Convert a "today" reference into a `CalendarDate` using local (never UTC) components.
- Add a whole number of days to a `CalendarDate`, returning a new `CalendarDate` (pure, no mutation).
- Resolve the weekend range relative to a reference date: Monday–Friday SHALL yield the coming Saturday..Sunday; Saturday SHALL yield today (Sat)..tomorrow (Sun); Sunday SHALL yield today..today.
- Parse an `<input type="date">` value (`"YYYY-MM-DD"`) into a `CalendarDate`, returning a sentinel "no value" result for empty or malformed input, and rejecting out-of-domain month (`< 1` or `> 12`) or day (`< 1` or `> 31`) components.
- Serialize a `CalendarDate` into a zero-padded `"YYYY-MM-DD"` string.
- Compute the inclusive whole-day span between two `CalendarDate`s (`1` when the two are equal).

These behaviors are the contract; the exact function names are an implementation detail owned by design.md.

#### Scenario: Weekend resolution follows the day-of-week rule

- **WHEN** the weekend range is resolved for a reference date that is a Wednesday
- **THEN** the resulting range SHALL start on the coming Saturday and end on the following Sunday
- **AND** WHEN the reference date is a Saturday, the range SHALL start that Saturday and end the next day (Sunday)
- **AND** WHEN the reference date is a Sunday, the range SHALL start and end on that same Sunday

#### Scenario: Inclusive day span counts both endpoints

- **WHEN** the inclusive day span is computed between two equal `CalendarDate`s
- **THEN** the result SHALL be `1`
- **AND** WHEN computed between a date and the date 29 days later, the result SHALL be `30`

#### Scenario: Malformed date-input value yields no `CalendarDate`

- **WHEN** an empty string or a value not matching `"YYYY-MM-DD"`, or a value whose month or day component is out of domain, is parsed
- **THEN** the library SHALL return its "no value" sentinel result and SHALL NOT return a `CalendarDate`

### Requirement: Invalid calendar components SHALL NOT silently roll over

When the library is asked to interpret a `CalendarDate` (or produce one from arithmetic) whose components do not denote a real calendar day (for example a zero or negative month, or a month/day outside its valid domain), it SHALL surface the invalidity as a rejection (a "no value" / null-equivalent result at the boundary) rather than silently normalizing it to a different real date. This closes the native-`Date` footgun where `new Date(2026, -1, 15)` rolls to 2025-12-15.

#### Scenario: Zero-month input does not roll into the previous year

- **WHEN** the library is asked to interpret a `CalendarDate` with `month = 0` (or any out-of-domain component)
- **THEN** it SHALL reject the value at the boundary (a "no value" / null-equivalent result)
- **AND** it SHALL NOT return a `CalendarDate` denoting a rolled-over date in an adjacent month or year

### Requirement: Two interchangeable engines SHALL satisfy the contract identically

The library SHALL ship with two engine implementations of the interface — one backed by the native `Date` object and one backed by `Temporal` (referencing `globalThis.Temporal`). A single shared differential test suite SHALL exercise BOTH engines against the same inputs and SHALL assert identical observable results for every operation in the contract, including the weekend rules, span math, parse/format round-trips, and the invalid-component rejection behavior. The `Temporal` engine SHALL NOT import a polyfill in its own module; the polyfill is a test-only dependency.

#### Scenario: Differential suite runs both engines and requires equivalence

- **WHEN** the shared plain-date test suite runs
- **THEN** every contract operation SHALL be executed against both the `Date` engine and the `Temporal` engine with the same inputs
- **AND** the two engines SHALL produce equal results for every case
- **AND** the suite SHALL fail if any input produces divergent results between the engines

#### Scenario: Temporal engine references the global, not a bundled polyfill

- **WHEN** the `Temporal` engine module source is inspected
- **THEN** it SHALL reference `globalThis.Temporal`
- **AND** it SHALL NOT import `@js-temporal/polyfill` (the polyfill is provided only by the test environment)

### Requirement: The active engine SHALL be selected at build time, defaulting to the `Date` engine

The library entry point SHALL resolve to exactly one engine per build via a build-time configuration (a Vite `resolve.alias` keyed on build mode/env), not a runtime branch. The default for development and production builds SHALL be the `Date` engine. Selecting the `Temporal` engine SHALL require an explicit build-time opt-in. Because selection is resolved at build time, the unselected engine SHALL be eliminated from the output by tree-shaking rather than shipped and branched at runtime.

#### Scenario: Default build resolves to the Date engine

- **WHEN** a production build is produced with no engine opt-in
- **THEN** the plain-date entry point SHALL resolve to the `Date` engine
- **AND** the `Temporal` engine module SHALL NOT be present in the emitted chunks

#### Scenario: Explicit opt-in resolves to the Temporal engine

- **WHEN** a build is produced with the documented `Temporal` engine opt-in set
- **THEN** the plain-date entry point SHALL resolve to the `Temporal` engine
- **AND** the `Date` engine module SHALL NOT be present in the emitted chunks

### Requirement: The production bundle SHALL contain no Temporal polyfill

The shipped production build SHALL NOT include any `@js-temporal/polyfill` / Temporal-polyfill code, keeping the change's bundle-size impact at zero relative to the pre-change baseline. The polyfill SHALL be declared as a `devDependencies`-only package. A CI check SHALL enforce this and fail the pipeline on regression.

#### Scenario: Built chunks are free of polyfill code

- **WHEN** the emitted production `dist/` chunks are scanned for `@js-temporal` / Temporal-polyfill identifiers
- **THEN** zero occurrences SHALL be found

#### Scenario: Polyfill is a dev-only dependency

- **WHEN** `frontend/package.json` is inspected
- **THEN** `@js-temporal/polyfill` SHALL appear under `devDependencies`
- **AND** SHALL NOT appear under `dependencies`

#### Scenario: CI guards the bundle-purity property

- **WHEN** a change causes the production bundle to include Temporal-polyfill code
- **THEN** the dedicated CI bundle-purity check SHALL fail

