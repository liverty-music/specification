## ADDED Requirements

### Requirement: Navigation bar size

The navigation bar SHALL be 64 px tall, not counting the safe area of the device, as in Material 3 Expressive. Tab icons SHALL be 24 px and tab labels SHALL use the label-medium style.

#### Scenario: Bar height

- **WHEN** a screen with the navigation bar is opened on a phone without a bottom safe area
- **THEN** the bar is 64 px tall

#### Scenario: Bar on a phone with a home indicator

- **WHEN** the same screen is opened on a phone with a bottom safe area
- **THEN** the bar is 64 px tall plus the safe area, and the tabs stay above the safe area
