# Spec Delta

## ADDED Requirements

### Requirement: Store a sale with its ticket types

Create SHALL store the sale without a draw time and every one of its TicketTypes together, or nothing, and return the sale with its TicketTypes; each TicketType of a FirstCome sale SHALL start with a sold count of 0. It SHALL fail with InvalidArgument when the sale or a TicketType breaks the TicketSale or TicketType rules, or when two of its TicketTypes are for the same event, and with FailedPrecondition when the Series or an event of a TicketType does not exist.

#### Scenario: Sale stored
- **WHEN** Create is called for an existing Series with TicketTypes for two of its events
- **THEN** the sale and both TicketTypes are stored and returned, and the sale is not drawn

#### Scenario: First-come sale stored
- **WHEN** a valid FirstCome sale with one TicketType of 150 tickets is created
- **THEN** it is stored with its TicketType at a sold count of 0

#### Scenario: Unknown event
- **WHEN** one TicketType names an event that does not exist
- **THEN** Create fails with FailedPrecondition and stores neither the sale nor any TicketType

#### Scenario: Same event twice
- **WHEN** two TicketTypes of the sale are for the same event
- **THEN** Create fails with InvalidArgument and stores nothing

#### Scenario: Invalid ticket type
- **WHEN** a TicketType has a per-account limit of 11
- **THEN** Create fails with InvalidArgument and stores nothing

## REMOVED Requirements

### Requirement: One sale per event
**Reason**: An event can now be offered by several sales (a presale and a general sale), each with one TicketType for it; one sale also covers several events of a Series. Uniqueness is one TicketType per event within a sale, and two sales of one event must not overlap, which TicketSaleUseCase.Create checks.
**Migration**: "Store a sale with its ticket types" above; the overlap rule is in usecase/ticket-sale/create "Sales of one event never overlap".
