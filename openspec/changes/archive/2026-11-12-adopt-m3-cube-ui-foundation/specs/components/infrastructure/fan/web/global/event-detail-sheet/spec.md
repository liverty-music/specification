## MODIFIED Requirements

### Requirement: Ticket Status buttons accessibility

The ticket sale notification button and each status in the row SHALL be a button exposing whether it is selected (`aria-pressed`), with at most one of the five selected. Each status in the row SHALL have an accessible name made of its canonical label, and the notification button an accessible name made of its visible text; each SHALL have a tap target of at least 48px.

#### Scenario: Pressed state

- **WHEN** the fan's status for the event is Applied
- **THEN** the 申込済み button exposes `aria-pressed="true"`
- **AND** the four other buttons expose `aria-pressed="false"`

#### Scenario: Keyboard

- **WHEN** a keyboard user moves focus through the ticket section
- **THEN** each button the section shows (five, or four with Paid) is reached with Tab and activated with Enter or Space
