## Context

The All Nearby mode (shipped in passive-concert-discovery) renders a filter area above the `ConcertHighway` timetable. Today it stacks: an area-selector button on its own row, a four-chip date-preset group, and — when カスタム is selected — two labeled native date inputs that expand inline. The inline expansion and the full-width area row consume vertical/horizontal space that belongs to the timetable, and the native inputs are unlocalized.

The design was prototyped and reviewed interactively; the chosen direction is "compact chips in the bar, complex input in a bottom sheet". The `bottom-sheet` primitive and `user-home-selector` already exist and are reused. The date sheet emits the same `{ from, to }` `CalendarDate` pair the route already consumes, so no data-layer change is needed.

## Goals / Non-Goals

**Goals:**
- Keep the filter bar to a single, fixed-height row so the timetable is never squeezed.
- Reduce the date filter to a single chip that surfaces the current selection, with all options (presets + custom range) reachable in one tap.
- Make custom-range adjustment a short path: chip → edit dates → apply (no dropdown drill-down).
- Localize every date display to Japanese (`Intl.DateTimeFormat('ja-JP')`).
- Replace unnatural All Nearby Japanese copy with natural, native phrasing.

**Non-Goals:**
- No change to `ConcertService.ListByLocation`, the `CalendarDate` contract, or any backend/proto.
- No calendar/grid date-range picker widget (native `<input type="date">` inside the sheet is sufficient for MVP).
- No change to the mode toggle (My Timetable / All Nearby) shipped earlier.
- No new date presets beyond the existing three + custom.

## Decisions

### D1 — Filter bar = single row of two chips (area + date)
The bar always renders `[📍 <area> ▾]` and `[📅 <date> ▾]` on one line. The area chip opens the existing `user-home-selector`; the date chip opens the date-range sheet. No control expands the bar, so the timetable's height is constant across all filter states.

### D2 — One date-range bottom sheet holding presets AND editable dates
Tapping the date chip opens a single bottom sheet (shared `bottom-sheet`) containing: a quick-preset chip row (今週末 / 7日以内 / 30日以内) and directly-editable 開始 / 終了 `<input type="date">` fields plus an apply action. There is no intermediate dropdown/menu — presets and manual dates live together, so custom adjustment is chip → edit → apply.

**Rationale:** an earlier dropdown-menu variant put custom behind two taps (open menu → tap カスタム → then a picker). Co-locating presets and fields removes the drill-down while keeping the bar to one chip.

### D3 — Preset = apply-and-close; custom = edit-then-apply
Tapping a quick preset resolves the range, applies it, and closes the sheet in one tap (the common path). Editing a date field keeps the sheet open for adjustment; a primary "apply" action confirms the custom range. This matches the tap-economy the product owner asked for.

### D4 — Localize all date display via Intl.DateTimeFormat('ja-JP')
The chip label and any range text render through `Intl.DateTimeFormat('ja-JP', { month, day })` → `8/12〜8/20` (or a single day when from === to), and preset selections show their preset name. The unlocalized native input format is no longer the primary display; the native inputs remain only as the in-sheet editing control.

### D5 — Client-side range validation mirrors the server cap
The sheet validates live: `to` may not precede `from`, and the inclusive span may not exceed 30 days (matching the server's use-case cap). Invalid states show an inline hint and block apply; the `to` field's `min`/`max` also constrain the native picker.

### D6 — Natural Japanese copy pass
Audit and rewrite `allNearby.*` strings (mode title/toggle, area prompt, empty state, preset labels, range hint) into natural Japanese, keeping ja/en key parity.

## Risks / Trade-offs

- **[Bottom sheet vs inline for a quick date tweak]** A sheet is one extra surface vs inline fields. Mitigation: presets apply in a single tap; the sheet is the standard mobile pattern for multi-field input and preserves the timetable's space — a net win at mobile width.
- **[Native date input inside the sheet]** The native picker's own chrome is still OS-localized, but the always-visible chip and range text are guaranteed Japanese via Intl, so the user-facing summary is correct regardless of OS locale.
- **[Visual-regression baselines]** The dashboard snapshot changes intentionally; baselines must be regenerated on merge.
- **[Copy changes ripple to any tests asserting the old strings]** Update affected unit/E2E assertions in the same change.
