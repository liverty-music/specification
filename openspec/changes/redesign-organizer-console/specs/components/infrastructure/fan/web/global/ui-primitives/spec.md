# Spec Delta

## ADDED Requirements

### Requirement: Circular Progress Indicator

The system SHALL provide a `<circular-progress>` custom element, shared by the fan app and the organizer console, that shows an indeterminate Material 3 circular progress indicator: an arc that grows, shrinks and rotates on a circular track. It SHALL come in two sizes, 48 px (default) and 24 px for use inside a button, with a 4 px stroke at 48 px and a 3 px stroke at 24 px. The arc SHALL use the `primary` color role of the surrounding app unless the parent sets another color. It SHALL expose `role="progressbar"` with an accessible name that defaults to the localized word for loading and can be set by the page, and SHALL carry no value while indeterminate. Under `prefers-reduced-motion: reduce` it SHALL stop growing and shrinking and rotate at most once every 2 seconds.

#### Scenario: Default rendering

- **WHEN** `<circular-progress>` is rendered without attributes
- **THEN** a 48 px indeterminate circular indicator with a 4 px arc in the `primary` color is shown, exposed as a progressbar named for loading

#### Scenario: Inside a button

- **WHEN** `<circular-progress size="small">` is placed inside a pending button
- **THEN** a 24 px indicator with a 3 px arc in the button's content color is shown, and the button keeps its size

#### Scenario: Reduced motion

- **WHEN** `prefers-reduced-motion: reduce` is active
- **THEN** the arc keeps a fixed length and turns at most once every 2 seconds

#### Scenario: Identity verification in progress

- **WHEN** the fan app's identity verification callback screen waits for the result
- **THEN** it shows `<circular-progress>` with the waiting message

## MODIFIED Requirements

### Requirement: State Placeholder Component
The system SHALL provide a `<state-placeholder>` custom element for displaying empty, error, and informational states with a consistent centered layout.

#### Scenario: Rendering with icon only
- **WHEN** `<state-placeholder icon="music">` is rendered with slotted content
- **THEN** the component SHALL display an xl-sized svg-icon
- **AND** the slotted content SHALL be projected via `<au-slot>` below the icon
- **AND** the content SHALL be vertically and horizontally centered

#### Scenario: No icon
- **WHEN** `<state-placeholder>` is rendered without an `icon` attribute
- **THEN** no svg-icon SHALL be rendered
- **AND** only the slotted content SHALL be displayed

#### Scenario: Custom content via slot
- **WHEN** child content is placed inside `<state-placeholder>`
- **THEN** the content SHALL be projected via `<au-slot>`
- **AND** this SHALL allow pages to provide titles, descriptions, buttons, links, or `<circular-progress>` elements

## REMOVED Requirements

### Requirement: Loading Spinner Custom Element

**Reason**: Replaced by the Material 3 circular progress indicator shared with the organizer console; the spinner had one use.
**Migration**: The identity verification callback screen uses `<circular-progress>` (see "Circular Progress Indicator"); the `<loading-spinner>` element is removed.
