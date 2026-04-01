## MODIFIED Requirements

### Requirement: FAB Entry Animation

The FAB SHALL animate on first appearance to draw user attention, then display a continuous neon pulse in idle state.

#### Scenario: First appearance animation

- **WHEN** the FAB becomes visible for the first time in a session
- **THEN** the system SHALL animate the FAB sliding up from below (`translateY(150%) → translateY(0)`, 400ms ease-out)
- **AND** after the slide completes, a ripple ring SHALL animate outward and fade exactly 2 times, then stop
- **AND** after the entry animation, the idle state SHALL display a pulsing neon border/glow via `box-shadow` animation (`pwa-fab-neon-pulse`, 2.5s ease-in-out infinite)

#### Scenario: Reduced motion

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the system SHALL replace the slide-up and ripple with a simple `opacity: 0 → 1` fade
- **AND** the pulsing neon animation SHALL be suppressed; a static `box-shadow` glow SHALL be shown instead

#### Scenario: Tap feedback

- **WHEN** the user taps the FAB
- **THEN** the FAB SHALL briefly scale down (`scale(0.92)` for 50ms) then return to `scale(1)` over 100ms

---

### Requirement: FAB Icon Size

The FAB icon SHALL be rendered at `1.5rem × 1.5rem` to improve visual prominence within the button container.

#### Scenario: Icon is visually prominent

- **WHEN** the FAB is visible
- **THEN** the install icon SHALL be rendered at `1.5rem` (24px) inline and block size

---

### Requirement: FAB Accessibility State

The FAB SHALL correctly communicate its visibility state to assistive technology and be removed from the tab order when hidden.

#### Scenario: FAB is visible

- **WHEN** the FAB is visible (`isVisible = true`)
- **THEN** the button element SHALL NOT have an `aria-hidden` attribute
- **AND** the button element SHALL have `tabindex="0"`

#### Scenario: FAB is hidden

- **WHEN** the FAB is hidden (`isVisible = false`)
- **THEN** the button element SHALL have `aria-hidden="true"`
- **AND** the button element SHALL have `tabindex="-1"` to remove it from the tab order
