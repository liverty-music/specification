## ADDED Requirements

### Requirement: Reset to Top 50 control
The Discover tab SHALL provide a Reset control that returns the bubble field to the global Top 50 artists, independent of the user's followed artists. The control SHALL be an icon-only (refresh/reset) button rendered as the leading item of the genre-chips row, pinned with `position: sticky` so it remains visible while the genre chips scroll horizontally. The control SHALL expose an accessible label.

#### Scenario: Reset restores global Top 50
- **WHEN** the user activates the Reset control
- **THEN** the system SHALL replace the entire bubble pool with the global Top 50 artists fetched via `listTop(country, '', 50)`
- **AND** SHALL NOT use the follow-seeded similar-artist load path
- **AND** the followed artists SHALL be excluded from the displayed bubbles

#### Scenario: Reset clears active genre filter
- **WHEN** a genre chip is active and the user activates the Reset control
- **THEN** the system SHALL clear the active genre selection
- **AND** no genre chip SHALL remain in the active state after reset

#### Scenario: Reset control stays visible while chips scroll
- **WHEN** the genre-chips row is scrolled horizontally
- **THEN** the Reset control SHALL remain pinned and visible at the leading edge of the row
- **AND** the genre chips SHALL scroll underneath without obscuring the control

#### Scenario: Reset control is accessible
- **WHEN** assistive technology inspects the Reset control
- **THEN** the control SHALL expose a descriptive accessible label
- **AND** SHALL be operable as a button
