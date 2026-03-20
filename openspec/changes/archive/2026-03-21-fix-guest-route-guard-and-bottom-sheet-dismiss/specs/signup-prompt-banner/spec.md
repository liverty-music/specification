## ADDED Requirements

### Requirement: Banner Dismiss Button

The signup prompt banner SHALL include a dismiss button allowing the user to hide it without signing up.

#### Scenario: Dismiss button is rendered

- **WHEN** the signup prompt banner is visible
- **THEN** a × (close) button SHALL be rendered on the trailing edge of the banner
- **AND** the button SHALL use the `svg-icon` component with the `x` icon
- **AND** the button SHALL have `aria-label` set to the localized `common.dismiss` key

#### Scenario: User taps dismiss button

- **WHEN** the user taps the × button on the signup prompt banner
- **THEN** the component SHALL dispatch a `banner-dismissed` CustomEvent with `bubbles: true`
- **AND** the parent route SHALL handle the event by setting the banner visibility to `false`
- **AND** the banner SHALL be removed from the rendered output

#### Scenario: Dismiss is not persisted across page loads

- **WHEN** the user dismisses the banner and later navigates back to the page
- **THEN** the banner MAY re-appear (dismiss state is session-scoped, not persisted to localStorage)
