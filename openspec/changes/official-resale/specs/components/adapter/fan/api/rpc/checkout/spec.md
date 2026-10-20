## ADDED Requirements

### Requirement: A returned checkout says whether it is a resale checkout

Every Checkout returned by Start and Get SHALL say whether it is a resale Checkout, and SHALL NOT carry the ResaleListings it holds or anything about their users.

#### Scenario: Resale checkout started
- **WHEN** a signed-in fan calls Start for 1 ticket of a sold-out TicketType with a free listing
- **THEN** the returned Checkout says it is a resale Checkout and names no other fan
