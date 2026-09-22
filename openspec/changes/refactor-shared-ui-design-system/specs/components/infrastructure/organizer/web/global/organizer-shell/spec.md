## ADDED Requirements

### Requirement: Console persistent navigation with no dead-end screens

Each console (admin and organizer) SHALL present a **persistent navigation
shell** around every screen — providing at least a home/return affordance, the
current organization/user context, and sign-out — and **every screen SHALL be
reachable through navigation and offer a way back**. No screen SHALL be reachable
only by typing a URL.

#### Scenario: Every console screen has navigation and a way back

- **WHEN** an operator opens any screen in a console
- **THEN** a persistent navigation (home + current context + sign-out) is present, and the screen offers a back or breadcrumb path to where it came from

#### Scenario: A created resource's status is reachable without a URL

- **WHEN** a resource that has a status/detail screen exists (for example a configured lottery phase)
- **THEN** that screen is reachable from a listing or navigation entry, not only by entering its URL directly
