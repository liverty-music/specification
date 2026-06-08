## ADDED Requirements

### Requirement: Celebration Reveals the Timetable Behind the Text

The celebration overlay SHALL keep the completed dashboard timetable visible behind the celebration text rather than fully obscuring it, so the overlay reveals the payoff it is announcing. The overlay backdrop SHALL NOT apply a full-viewport opaque veil or a full-viewport blur of the content behind it. Darkening SHALL be localized to the region behind the heading and sub-text (a feathered "text-lens"), leaving the screen edges showing the timetable's colors. Regardless of the colors behind it — including the brightest stage cards — the heading and sub-text SHALL remain legible. This requirement governs only the overlay's backdrop and text-contrast treatment; it does not change the celebration tiers, gating, once-per-tier behavior, confetti flag, tap-to-dismiss, or reduced-motion handling defined by `Requirement: Two-Tier Celebration Overlay`.

#### Scenario: Timetable colors remain visible at the screen edges

- **WHEN** the celebration overlay is displayed over the loaded timetable
- **THEN** the timetable's card colors SHALL remain visible at the screen edges (outside the text region)
- **AND** the overlay SHALL NOT cover the viewport with an opaque veil or a full-viewport blur

#### Scenario: Heading and sub-text stay legible over bright cards

- **WHEN** the celebration overlay is displayed over bright/light-colored timetable cards (e.g. near-stage cyan)
- **THEN** both the heading and the sub-text SHALL remain legible against that background

#### Scenario: Existing celebration behavior is preserved

- **WHEN** the celebration overlay is shown in either tier (guest light or post-signup full)
- **THEN** the tier gating, at-most-once-per-tier persistence, confetti flag, tap-to-dismiss, and `prefers-reduced-motion` handling SHALL behave exactly as before this change
