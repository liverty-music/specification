# Concert Highway Custom Element

## Purpose

Reusable custom element that renders the 3-column concert lane grid (home/nearby/away) with stage headers, date separators, event cards, and laser beam effects. Used by both the authenticated dashboard and the Welcome page preview.

## Requirements

### Requirement: Concert Highway Custom Element

The system SHALL provide a reusable `<concert-highway>` custom element that renders a 3-column concert lane grid (home/nearby/away) with stage headers, date separators, event cards, and laser beam effects.

#### Scenario: Render date groups with 3-column layout

- **WHEN** `<concert-highway>` receives a `dateGroups` binding containing `DateGroup[]`
- **THEN** the CE SHALL render a 3-column grid with stage headers labeled HOME, NEAR, and AWAY
- **AND** each date group SHALL display a sticky date separator followed by three lane columns containing `<event-card>` components

#### Scenario: Laser beam effects for matched events

- **WHEN** `showBeams` is true (default) and the date groups contain matched events
- **THEN** the CE SHALL render laser beam overlays from the top of the viewport to each matched event card
- **AND** beam positions SHALL update on scroll via `requestAnimationFrame`

#### Scenario: Readonly mode suppresses card interaction

- **WHEN** `readonly` is set to true
- **THEN** all `<event-card>` components SHALL be rendered with `readonly="true"`
- **AND** tapping a card SHALL NOT dispatch the `event-selected` event

#### Scenario: Interactive mode dispatches event selection

- **WHEN** `readonly` is false and the user taps an event card
- **THEN** the `event-selected` custom event SHALL bubble up from the CE
- **AND** the event detail payload SHALL contain the selected `Concert` object

#### Scenario: Empty lane display

- **WHEN** a lane (home, nearby, or away) has no concerts for a given date
- **THEN** the lane SHALL display a placeholder dash ("—")
