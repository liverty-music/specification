## Why

The Dashboard "All Nearby" filter UI shipped functional but space-inefficient, and prod use surfaced concrete UX problems:

- Choosing the **カスタム** date preset expands two stacked, labeled `<input type="date">` fields inline, growing the filter area and **squeezing the concert timetable** — the screen's primary content.
- The native date inputs render an **unlocalized US `MM/DD/YYYY`** format for Japanese users.
- The **area selector occupies its own full row**, wasting horizontal space.
- The **four date presets are four separate chips**, consuming horizontal width for a single-select choice.
- Several **All Nearby Japanese strings read unnaturally** (machine-translation feel).

The feature is otherwise complete and in production; this change is a frontend-only UX refinement (no proto or backend change).

## What Changes

- The All Nearby filter bar becomes a **single row of two chips**: an **area chip** and a **single date chip** — no inline expansion, so the timetable height is never reduced.
- The date chip opens **one date-range bottom sheet** (reusing the shared bottom-sheet primitive) that holds BOTH quick presets (今週末 / 7日以内 / 30日以内) AND directly-editable start/end date fields with live validation (`from ≤ to`, span ≤ 30 days). Adjusting a custom range is chip → edit → apply — no drill-down.
- Quick presets apply immediately and close the sheet; custom edits confirm via an apply action.
- The date chip label and every range display are **localized with `Intl.DateTimeFormat('ja-JP')`** (e.g. `8/12〜8/20`), replacing the unlocalized native format.
- The **All Nearby Japanese i18n copy is audited and rewritten** into natural, native Japanese (mode titles/toggle, area prompt, empty state, date-preset labels, range hints).

Grounded in mobile UI best practice (Material 3 date-pickers & chips, Apple HIG segmented/date controls, NNG/UXPin filter guidance): present filters as compact chips and move complex/multi-field input into a bottom sheet rather than expanding it inline. Validated with an interactive prototype and the direction confirmed with the product owner.

## Capabilities

### New Capabilities

<!-- none — this refines existing All Nearby behavior -->

### Modified Capabilities

- `passive-concert-discovery`: Replaces the inline "Date Preset Selector" and standalone "Area Selector" requirements with a compact single-row filter (area chip + single date chip → date-range bottom sheet with presets + editable, validated, localized range); adds a localized-date-formatting requirement; requires natural Japanese copy for the All Nearby surface.

## Impact

- **Frontend only** (`liverty-music/frontend`); no proto, backend, or BSR change.
- Components: `date-preset-selector` (replaced by a date chip + date-range bottom sheet built on the shared `bottom-sheet` primitive), `dashboard-route` (filter bar wiring), the area chip, and the `allNearby.*` i18n keys (ja + en).
- No change to `ConcertService.ListByLocation` or the `CalendarDate` contract — the sheet still emits a `{ from, to }` `CalendarDate` pair.
- Visual-regression baselines for the dashboard will need regeneration (intentional UI change).
