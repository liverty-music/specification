# Spec Delta

## ADDED Requirements

### Requirement: The screen's address

The checkout of one seat type of a first-come sale SHALL be served at `/concerts/<id>/checkout?stock=<stockId>`, where `<id>` is the Event and `<stockId>` the TicketStock; the concert page's buy action for that seat type opens it.

#### Scenario: Opening checkout from the concert page
- **WHEN** a fan taps the buy action of the 3000 yen seat type on `/concerts/<id>`
- **THEN** the app shows the checkout at `/concerts/<id>/checkout?stock=<id of that seat type>`
