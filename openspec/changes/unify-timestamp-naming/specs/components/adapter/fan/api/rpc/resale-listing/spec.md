# Spec Delta

## MODIFIED Requirements

### Requirement: A returned listing shows only the fan's own side

A ResaleListing returned by the fan boundary SHALL carry its id, Ticket, price, resale fee, refund amount, status (Listed, Sold, Withdrawn, Cancelled or Expired), create time, close time, sell time and refund time. It SHALL NOT carry the Checkout that holds it or anything about the fan who bought it.

#### Scenario: Sold listing
- **WHEN** List returns a Sold listing
- **THEN** it carries its price, fee, refund amount, sell time and refund time, and nothing about the fan who bought it
