# Spec Delta

## ADDED Requirements

### Requirement: The screen's address

The lottery entry form for one seat type of a lottery sale SHALL be served at `/concerts/<id>/lottery-entries/new?sale=<saleId>&stock=<stockId>`; the concert page's entry action for that seat type opens it. After the entry is confirmed, the form's confirmation SHALL link to the fan's entries in that sale at `/concerts/<id>/lottery-entries?sale=<saleId>`.

#### Scenario: Opening the entry form
- **WHEN** a fan taps the entry action of a seat type on `/concerts/<id>`
- **THEN** the app shows the form at `/concerts/<id>/lottery-entries/new?sale=<saleId>&stock=<stockId>`

#### Scenario: After confirming
- **WHEN** the fan confirms the entry
- **THEN** the confirmation links to `/concerts/<id>/lottery-entries?sale=<saleId>`
