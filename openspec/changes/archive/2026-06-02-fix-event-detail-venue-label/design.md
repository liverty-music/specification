## Context

The frontend `Concert` entity (aliased as `LiveEvent`) is produced by the RPC mapper (`concert-mapper.ts`) from the proto `Concert`. Today the mapper emits two region fields:

- `locationLabel: string` — the human-readable localized prefecture name (e.g. `東京都`), computed via `displayName(adminArea)`.
- `adminArea?: string` — the raw ISO 3166-2 subdivision code (e.g. `JP-13`), copied straight from the proto.

A code audit shows the raw `adminArea` on the entity has exactly one presentation-layer consumer: `event-detail-sheet.ts`'s `googleMapsUrl`, which computes `displayName(this.event.adminArea)` — the same derivation the mapper already performed into `locationLabel`. Dashboard lane assignment does NOT read the entity's `adminArea`; lanes come from `hypeLevel`/`matched`, which are derived upstream and passed into the mapper as arguments. The detail sheet's venue line erroneously binds the raw `adminArea`, surfacing `JP-13` to users.

So the raw code provides no unique value to the presentation layer, yet its presence forced the UI to choose between code and label — and the template chose wrong.

## Goals / Non-Goals

**Goals:**
- Make the layering correct: the adapter is the single owner of the proto-code → user-facing-label translation; the presentation entity exposes only the display-ready label.
- Eliminate the class of bug where a component can accidentally render an internal code.
- The detail sheet shows the localized prefecture name in both the venue line and the Google Maps query.

**Non-Goals:**
- No proto/backend/BSR change — the raw `admin_area` still exists in the proto.
- No change to lane-assignment logic.
- No change to the `displayName` helper itself.
- The ticket journey status UI redesign is a separate change.

## Decisions

- **Drop `adminArea` from the presentation `Concert` entity.** The adapter already produces the presentation-ready `locationLabel`; carrying the raw code alongside it is what let the UI render the wrong value. Removing it makes the wrong choice structurally impossible. Alternative considered: keep `adminArea` on the entity but forbid templates from binding it (convention/lint) — rejected because it preserves the dual-field temptation and relies on discipline rather than the type system. Alternative considered: minimal one-line template fix — rejected because it leaves the redundant re-derivation and the latent dual-field hazard in place.
- **`googleMapsUrl` consumes `locationLabel` directly.** The query component was already `displayName(adminArea)` ≡ `locationLabel`, so behavior is unchanged; the component no longer imports `displayName`. The mapper keeps a local `adminArea` variable solely to derive `locationLabel`.
- **Conditional render guards on `locationLabel`.** `locationLabel` is a non-optional `string` that is empty (`''`) when the proto has no admin area, so the venue line's `if.bind` uses a truthiness check on `locationLabel` — an empty string correctly omits the line.

## Risks / Trade-offs

- [A future feature needs the raw code on the entity for code-level comparison] → The proto still carries `admin_area`; re-add a typed field at the adapter boundary if and when a real consumer appears. YAGNI: nothing currently reads it. Mitigation: documented here.
- [`locationLabel` empty for an unmapped/unknown code] → `displayName` falls back to returning its input when no prefecture entry matches, mirroring existing card behavior; out of scope to redesign the fallback (owned by `admin-area-normalization`).
- [Tests assert on the removed `adminArea`] → `concert-mapper.spec.ts` and `event-detail-sheet.spec.ts` reference `adminArea`; update them to assert `locationLabel`. Verified via `make check` and the visual-baseline workflow.
