## MODIFIED Requirements

### Requirement: Interactive Timetable Detail

The landing page SHALL present the concert auto-collection pillar as the product's own timetable, rendered as a complete composed frame, and SHALL make its concert cards interactive so that activating a card opens the product's real concert detail view. The detail view SHALL surface the official-information link, venue information, and the calendar affordance. Controls that require authentication (such as the ticket-journey tracker) SHALL NOT be shown to the anonymous visitor. The landing page SHALL guide the visitor to this interaction rather than relying on a hover-only affordance.

#### Scenario: Timetable shown as a composed frame

- **WHEN** an unauthenticated user reaches the timetable and preview data is available
- **THEN** the system SHALL display the concert timetable as a complete composed frame, not a cropped peek
- **AND** the system SHALL communicate that this timetable is auto-collected from the user's followed artists

#### Scenario: Guidance to open a concert

- **WHEN** the timetable becomes interactive in the demo
- **THEN** the system SHALL surface a guidance affordance directing the visitor to open a concert card
- **AND** the guidance SHALL NOT depend on a pointer hover state

#### Scenario: Card opens the real detail view

- **WHEN** the unauthenticated user activates a concert card
- **THEN** the system SHALL open the product's real concert detail view for that concert
- **AND** the view SHALL surface official-information, venue, and calendar affordances
- **AND** the system SHALL NOT display authentication-gated controls such as the ticket-journey tracker

#### Scenario: Timetable absent without preview data

- **WHEN** preview data is unavailable
- **THEN** the system SHALL NOT render the demo or the timetable
- **AND** the landing page SHALL fall back to the hero inline CTA behavior defined by `Passkey Authentication CTA`
