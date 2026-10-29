# Spec Delta

## ADDED Requirements

### Requirement: Get returns the sale and its events

Get SHALL return the TicketSale with the given id with the events it names, and SHALL fail with NotFound when no TicketSale has the id.

#### Scenario: Sale covering several events

- **WHEN** Get is called with the id of a sale that names two events
- **THEN** that sale is returned with both events

#### Scenario: Unknown sale

- **WHEN** no TicketSale has the id
- **THEN** Get fails with NotFound

## REMOVED Requirements

### Requirement: Get returns the sale and its held count

**Reason**: A TicketSale has no TicketTypes; held counts belong to TicketStocks.
**Migration**: See "Get returns the sale and its events" and components/entity/ticket-stock/get.
