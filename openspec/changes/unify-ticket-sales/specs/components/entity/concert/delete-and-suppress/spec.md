# Spec Delta

## MODIFIED Requirements

### Requirement: Delete and suppress together

DeleteAndSuppress SHALL remove the Event and, with it, its performers, its Concert, its TicketJourneys, and its TicketTypes with their lottery entries, and every TicketSale left without a TicketType, and SHALL record a SuppressedConcert for the removed Event's Venue, date and start time. Both effects SHALL happen together or not at all. The Event's Series and the Series' SalesPhases SHALL remain.

#### Scenario: Concert with fan journeys
- **WHEN** a Concert that fans track in TicketJourneys is deleted
- **THEN** the Event and those TicketJourneys are removed and its slot is suppressed

#### Scenario: Series stays
- **WHEN** one Event of a Series with SalesPhases is deleted
- **THEN** the Series and its SalesPhases remain
