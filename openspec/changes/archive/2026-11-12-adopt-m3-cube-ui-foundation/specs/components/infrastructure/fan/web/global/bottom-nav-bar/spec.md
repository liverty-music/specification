## ADDED Requirements

### Requirement: Navigation bar size

The navigation bar SHALL be 64 px tall, not counting the safe area of the device, as in Material 3 Expressive. Tab icons SHALL be 24 px and tab labels SHALL use the label-medium style. On a bar narrower than 360 px, where four label-medium labels and the floating button do not fit side by side, the labels SHALL use the label-small size with no letter spacing instead (measured with Noto Sans JP, label-small alone leaves 1.5 px between two labels), so that no two labels touch and no tab's touch target overlaps the floating button.

#### Scenario: Bar height

- **WHEN** a screen with the navigation bar is opened on a phone without a bottom safe area
- **THEN** the bar is 64 px tall

#### Scenario: Bar on a phone with a home indicator

- **WHEN** the same screen is opened on a phone with a bottom safe area
- **THEN** the bar is 64 px tall plus the safe area, and the tabs stay above the safe area

#### Scenario: Bar on a 320 px screen

- **WHEN** a screen with the navigation bar is opened on a 320 px wide phone
- **THEN** the tab labels use the label-small size with no letter spacing, no two labels are closer than 4 px, and a tap in any tab's 48 px target never lands on the floating button

## MODIFIED Requirements

### Requirement: Animated selection state

Selection controls (bottom-nav tabs, filter chips) SHALL animate into the selected state driven by a real
selection attribute (not hover), with a reduced-motion fallback. A shape morph SHALL be used only where it
reads as intentional: the bottom-nav tab morphs rounder with a spatial spring. Filter chips SHALL NOT
shape-morph — a Material 3 chip keeps its shape in every state; instead a chip signals selection with the
`secondary-container` fill and a leading checkmark.

#### Scenario: Selecting a nav tab springs into state

- **WHEN** a user selects a navigation tab
- **THEN** the selected tab animates into its selected treatment — color plus a spatial-spring shape morph
  (rounder) — rather than switching statically

#### Scenario: Selecting a filter chip is clearly signalled without a shape morph

- **WHEN** a user selects a filter chip
- **THEN** the chip takes its selected treatment via the `secondary-container` fill and a leading checkmark
  (its shape is unchanged), avoiding a radius tween

#### Scenario: Selection is driven by state, not hover

- **WHEN** the selected treatment is evaluated
- **THEN** it reflects the actual selected/`aria`-state attribute and does not trigger on hover alone
