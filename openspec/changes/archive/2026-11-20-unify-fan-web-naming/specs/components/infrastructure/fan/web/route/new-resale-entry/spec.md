# Spec Delta

## ADDED Requirements

### Requirement: The screen's address

The official resale application for one sold-out seat type SHALL be served at `/concerts/<id>/resale-entries/new?stock=<stockId>`; the concert page's resale action for that seat type and the apply-again action on the resale entries screen open it.

#### Scenario: Opening the application
- **WHEN** a fan taps the resale action of a sold-out seat type on `/concerts/<id>`
- **THEN** the app shows the application at `/concerts/<id>/resale-entries/new?stock=<stockId>`
