## ADDED Requirements

### Requirement: The update action button SHALL be visually prominent

When the update snack is displayed, its action button (labelled with `pwa.updateAction`) SHALL be visually distinguished from the snack body text so that users can immediately identify it as a primary call-to-action. The button SHALL use a pill-shaped border and a pulsing glow animation to attract attention. The animation SHALL be suppressed when `prefers-reduced-motion: reduce` is active.

#### Scenario: Action button appears as a pill with pulse animation

- **WHEN** the update snack is visible with the action button
- **THEN** the action button SHALL have a rounded pill border (1.5px, semi-transparent white)
- **AND** a semi-transparent white background fill SHALL distinguish it from plain text
- **AND** the button SHALL animate a repeating `box-shadow` glow pulse (period ≈ 1.8s, ease-in-out)

#### Scenario: Animation is suppressed under reduced motion

- **WHEN** the user's OS has `prefers-reduced-motion: reduce` set
- **THEN** the pulse animation SHALL NOT play
- **AND** the pill border and background fill SHALL still be applied (static emphasis)
