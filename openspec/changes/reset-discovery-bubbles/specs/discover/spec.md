## ADDED Requirements

### Requirement: Reset to Top 50 control
The Discover tab SHALL provide a Reset control that returns the bubble field to the global Top 50 artists, independent of the user's followed artists. The control SHALL be an icon-only (refresh/reset) button placed at the leading edge of the genre row as a fixed sibling beside the horizontally-scrollable genre chips, so it remains visible while the chips scroll. The control SHALL expose an accessible label.

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
- **WHEN** the genre chips are scrolled horizontally
- **THEN** the Reset control SHALL remain visible at the leading edge of the genre row
- **AND** the genre chips SHALL scroll within their own container beside the control, never overlapping or obscuring it

#### Scenario: Reset control is accessible
- **WHEN** assistive technology inspects the Reset control
- **THEN** the control SHALL expose a descriptive accessible label
- **AND** SHALL be operable as a button
