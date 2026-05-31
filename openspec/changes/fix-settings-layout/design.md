# Design

## Settings content slides under the fixed header

### Root cause

The route box is a 2-row grid (`auto 1fr`) with the `page-header` pinned to the
`header` row and `main` in the `content` (`1fr`) row:

```
settings-route   block-size: 100%   (= app-shell viewport track minmax(0,1fr))
└ display: grid  rows: auto / 1fr
   ├─[header]  page-header           grid-area: header  (fixed)
   └─[content] main                  1fr track, scroll container
                ↑ grid item default min-block-size: auto
                  → main refuses to shrink below content height
                  → 1fr track grows to full content height
                  → grid exceeds the route's 100% box
                  → no overflow guard on :scope → content overflows upward,
                    first card + section title end up behind page-header
```

`overflow-y: auto` on `main` cannot engage because the item never gets a
height smaller than its content — the classic CSS min-size gotcha: a flex/grid
item's automatic minimum size is `auto`, not `0`.

### Sibling routes (the canonical pattern)

| route       | `:scope` rows         | `main` overflow | `main` min-block-size | scroll element                        |
|-------------|-----------------------|-----------------|-----------------------|---------------------------------------|
| my-artists  | `auto 1fr`            | `hidden`        | `0`                   | inner child                           |
| dashboard   | `auto minmax(0,1fr)`  | `hidden`        | `0`                   | inner child                           |
| tickets     | `auto 1fr`            | `hidden`        | `0`                   | `.ticket-list` `flex:1; overflow-y:auto` |
| discovery   | `auto 1fr`            | `hidden`        | (child `block-size:100%`) | inner child                       |
| **settings**| `auto 1fr`            | **`auto`**      | **missing**           | `main` itself                         |

### Decision

Adopt the house pattern rather than the minimal one-liner:

- `main`: `overflow: hidden; min-block-size: 0;` (shell, no scrolling itself).
- Introduce an inner scroll container (`.settings-scroll`, `flex: 1;
  overflow-y: auto;`) that holds the `<section>` list, with the existing
  padding gutters.

Rationale: the one-line fix (just add `min-block-size: 0` to the
`overflow-y: auto` main) would also work visually, but keeping Settings
structurally identical to its four siblings removes the divergence that caused
the regression and prevents recurrence when the page is next edited.

## CUBE CSS alignment

- **Composition re-use:** the section list's vertical rhythm comes from the
  existing `[ stack ]` composition primitive (compositions.css), grouped as
  `[ settings-scroll ] [ stack ]`; the language list as
  `[ language-list ] [ stack ]` with a `--stack-gap` exception for its tighter
  rhythm. The block layer keeps only skin/scroll/gutters — it does NOT
  re-declare `display`/`flex-direction`/`gap` (block wins over composition in
  the `reset, tokens, global, composition, utility, block, exception` order, so
  re-declaring would silently override the primitive).
- **Bracket grouping:** drop `class="[ settings-divider ]"` (a lone block class
  in brackets is meaningless). Use brackets only to group
  `[ block ] [ composition ] [ utilities ]` by role, per `consent-route` (the
  in-repo canonical, e.g. `class="[ consent-card ] [ flow ]"`).

## Out of scope

- The guest language-selector reactivity defect (selector highlight not
  following the active locale after a guest change) is NOT addressed here. Its
  root cause is the dual-owner guest/authed state model (`GuestService` vs
  `UserService`); the proper fix is the GuestService dissolution refactor,
  tracked as a separate change. Until that lands, the guest selector highlight
  remains stale.
- The PostHog CSP `Fetch API cannot load …eu.i.posthog.com` console errors seen
  in the same devtools capture are a separate analytics/CSP concern.
- No change to home-area selection, push, sound, consent, or account sections
  beyond the composition/skin refactor needed for the layout fix.
