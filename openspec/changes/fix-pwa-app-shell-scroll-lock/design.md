## Context

The `app-shell` uses a `100dvh` CSS Grid (`"viewport" 1fr / "nav" auto`) with a non-fixed bottom nav bar — a standard-conformant app-shell skeleton. `viewport-fit=cover` and `env(safe-area-inset-*)` are already handled. Scrolling is intended to happen only inside the concert list (`minmax(0, 1fr)` track → inner scroller).

However, the document root can still scroll:

- `reset.css` sets `body { min-block-size: 100dvh }` with no `overflow` control on `html`/`body`.
- No `overscroll-behavior` is declared at the root.

Because `app-shell` is exactly `100dvh` and `body` is `min-block-size: 100dvh`, any transient where the dynamic viewport unit resolves larger than the visible area (which the standalone pull-to-refresh / overscroll gesture induces) leaves `body` with a few pixels of scroll range. With no root scroll lock and no `overscroll-behavior`, that scrolled state persists: the shell becomes taller than the visible viewport and the header row and the bottom nav become mutually exclusive on screen.

The web-standard remedy for this (per modern CSS layout guidance: viewport-unit mechanics + `overscroll-behavior`) is the "fixed app shell + single inner scroller" pattern: make the document root a non-scrolling frame and confine all scrolling to one inner container.

## Goals / Non-Goals

**Goals:**
- The bottom nav bar and header remain simultaneously visible and pinned regardless of pull-to-refresh / overscroll in the installed standalone PWA.
- The document root (`html`/`body`) is never a scroll source.
- All scrolling is confined to the single inner concert scroller; scroll chaining never reaches the document.

**Non-Goals:**
- No change to the `app-shell` grid structure, `100dvh` sizing, `viewport-fit=cover`, or safe-area handling — those are already standard-conformant.
- No change to page-transition animations, nav visibility logic, or route structure.
- No new data-refresh UI to replace the disabled native pull-to-refresh (out of scope; the app already has its own reload paths).

## Decisions

- **Root scroll lock over per-element patching.** Set `html, body { block-size: 100%; overflow: hidden; overscroll-behavior: none; }` and remove `body { min-block-size: 100dvh }`. Making the root a fixed frame is the robust, standard pattern; it removes the scroll source entirely rather than chasing `dvh` fluctuations.
  - Alternative considered: keep `body` scrollable but add only `overscroll-behavior: none`. Rejected — it neutralizes the gesture but leaves `body` able to scroll whenever `dvh` momentarily exceeds the visible viewport, so the shift can still occur.
  - Alternative considered: `app-shell { position: fixed; inset: 0 }`. Rejected as more invasive than a root lock and redundant once the root cannot scroll; the existing `100dvh` grid already owns height correctly.

- **Keep `app-shell` height as the single height owner.** With the root locked, `body { min-block-size: 100dvh }` is redundant and is the concrete scroll source, so it is removed. `app-shell` keeps `block-size: 100dvh`.

- **`overscroll-behavior: contain` on the inner scroller.** Add it to the concert list scroll container (`.concert-scroll`) so a scroll-boundary bounce never chains into the (now non-scrolling) document. This is defense-in-depth alongside the root lock.

- **`overscroll-behavior: none` at root disables native pull-to-refresh.** This is intentional and acceptable: the product is an installed home-screen PWA and the accidental full reload from pull-to-refresh is itself a source of the reported bug.

## Risks / Trade-offs

- [Native pull-to-refresh reload is disabled in the standalone PWA] → Acceptable and intended; the app provides its own data-refresh paths. If an explicit refresh affordance is later desired, add it as in-app UI (separate change).
- [`overflow: hidden` on `html`/`body` could clip a route that (incorrectly) relies on document scroll] → All routes already delegate scrolling to inner containers per the existing shell-layout requirements; verify no route depends on document-level scroll during QA.
- [`dvh` behavior differs across iOS Safari (home-screen) vs Android Chrome (installed)] → The root lock makes the fix independent of `dvh` dynamics, so both targets are covered; still verify on both during rollout.

## Migration Plan

1. Edit `src/styles/reset.css`: add root scroll-lock rule on `html, body`; remove `body { min-block-size: 100dvh }`.
2. Add `overscroll-behavior: contain` to `.concert-scroll`.
3. Confirm `app-shell.css` remains the height owner (`block-size: 100dvh`), no change required.
4. Extend layout/shell E2E assertions to verify nav+header stay pinned after an overscroll gesture in a standalone-emulated viewport.
5. `make check` (Biome + stylelint + typecheck + tests), then ship via the frontend PR → release path.

Rollback: revert the CSS change (single-commit, no data or API impact).

## Open Questions

- Which element is the canonical inner scroller in the current tree — `.concert-scroll` (as in `shell-layout` spec) vs the live-highway variant found in code? Confirm during apply and attach `overscroll-behavior: contain` to the actual scroll container.
- Should other scrollable routes (e.g., settings, my-artists lists) also receive `overscroll-behavior: contain`, or is the root lock sufficient for them? Default: root lock covers them; add per-container only if a boundary-bounce artifact is observed.
