## Context

Post-review polish of the onboarding flow frontend. All changes are isolated to `frontend/src/` with no backend or API impact. The onboarding-flow-final.md (2026-03-24) is the source of truth for expected behavior.

## Goals / Non-Goals

**Goals:**
- Reduce DNA orb max size so bubbles have more room on mobile
- Fix lane intro sequencing to match the spec (coach mark → Home Selector)
- Remove non-spec UI elements (artist count badge)
- Improve signup banner mobile usability

**Non-Goals:**
- Changing the bubble sizing or physics (only the central orb changes)
- Modifying the lane intro content or phases (only the order of coach mark vs Home Selector)
- Any backend or API changes

## Decisions

### 1. DNA Orb Growth Curve

Current: `BASE=60, GROWTH=12, LINEAR_STEPS=5, MAX=120` → max at follow 5.

New: `BASE=60, GROWTH=7.5, LINEAR_STEPS=4, MAX=90` → max at follow 4.

```
Follow   Current   New
  0        60       60
  1        72       67.5
  2        84       75
  3        96       82.5
  4       108       90 (MAX)
  5       120       90
```

Rationale: MAX=90 keeps the orb visually prominent while freeing ~60px diameter of bubble space. Reaching MAX at 4 follows (instead of 5) ensures users see full orb growth within the discovery threshold (5 follows or 3 with concerts).

The logarithmic tail for follow 5+ now caps at 90 — the `Math.min(MAX_RADIUS, ...)` already handles this.

### 2. orbZoneHeight reduction

Current: `orbZoneHeight = 160`. This is the physics wall that prevents bubbles from entering the orb zone.

With MAX_RADIUS dropping from 120 to 90, reduce `orbZoneHeight` from 160 to 130. This reclaims ~30px of vertical space for the bubble area.

The orb's visual footprint (including glow at `renderRadius * 1.6`) at MAX=90 with breath is approximately `90 * 1.05 * 1.6 ≈ 151px` from center — the 130px wall height plus the orb's Y position (`canvasHeight - 80`) provides sufficient clearance.

### 3. Lane Intro: HOME STAGE Context via Home Selector Description

Current behavior in `startLaneIntro()`:
```
needsRegion=true → laneIntroPhase='waiting-for-home' → homeSelector.open()
```
Home Selector opens immediately with a generic description that doesn't explain the HOME STAGE concept.

Approach: Keep the same `waiting-for-home` → `homeSelector.open()` flow, but update the Home Selector's i18n description text (`userHome.description`) to include the HOME STAGE explanation. This avoids the z-index overlap between the bottom-sheet and coach mark spotlight that occurs on mobile when both are shown simultaneously. The coach mark spotlight is only activated after home selection, when concert data loads and stage headers appear in the DOM.

The existing `@watch` on `dateGroups.length` handles the transition after home selection — no change needed there.

### 4. Remove Artist Count from My Artists Header

The `<span class="artist-count">(${artists.length})</span>` in `my-artists-route.html` line 4 is not in any spec. Remove the element and any associated CSS.

### 5. Signup Banner Vertical Layout

Change `.signup-banner` from `flex-direction: row` to `column`. The CTA button becomes full-width below the message text. The dismiss button moves to the top-right corner of the text row (absolute positioned or inline with text).

```
Before:                          After:
┌─────────────────────────┐     ┌─────────────────────────────┐
│ Text...  [CTA] [×]      │     │ Text message here...      × │
└─────────────────────────┘     │ [     CTA Button          ] │
                                └─────────────────────────────┘
```

## Risks / Trade-offs

- **Orb size reduction may feel less impressive** → Mitigated by maintaining the 2x growth ratio (60→90 is 1.5x, but with glow effects the visual presence remains strong)
- **orbZoneHeight=130 may allow bubble-orb overlap at high follow counts** → The orb position is fixed at `canvasHeight - 80`, and the wall at `canvasHeight - 130` gives 50px clearance from orb center, which exceeds the max physical bubble radius (45px)
- **Lane intro coach mark + Home Selector simultaneously may feel busy** → The coach mark provides context for _why_ the selector appears, which is better UX than a sudden modal
