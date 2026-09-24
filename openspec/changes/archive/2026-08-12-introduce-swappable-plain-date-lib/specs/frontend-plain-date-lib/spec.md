## Purpose

This capability defines the SPA's implementation-agnostic calendar-arithmetic library: a single seam through which all pure "civil date" math (weekend/range preset resolution, `<input type="date">` parse/format, inclusive day-span, `CalendarDate` conversions) flows. It fixes one behavioral contract that two interchangeable engines — a native `Date` engine (shipped today) and a `Temporal` engine (shipped when Baseline) — SHALL satisfy identically, so the frontend can migrate from `Date` to `Temporal` at build time without any behavior change and without a production bundle-size regression.

## ADDED Requirements

### Requirement: Invalid calendar components SHALL NOT silently roll over

When the library is asked to interpret a `CalendarDate` (or produce one from arithmetic) whose components do not denote a real calendar day (for example a zero or negative month, or a month/day outside its valid domain), it SHALL surface the invalidity as a rejection (a "no value" / null-equivalent result at the boundary) rather than silently normalizing it to a different real date. This closes the native-`Date` footgun where `new Date(2026, -1, 15)` rolls to 2025-12-15.

#### Scenario: Zero-month input does not roll into the previous year

- **WHEN** the library is asked to interpret a `CalendarDate` with `month = 0` (or any out-of-domain component)
- **THEN** it SHALL reject the value at the boundary (a "no value" / null-equivalent result)
- **AND** it SHALL NOT return a `CalendarDate` denoting a rolled-over date in an adjacent month or year
