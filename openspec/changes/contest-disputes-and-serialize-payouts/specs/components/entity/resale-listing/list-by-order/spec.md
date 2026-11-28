# Spec Delta

## Purpose

Lists every resale listing of one Order's Tickets, with the refund each Sold one paid the Order's user.

## ADDED Requirements

### Requirement: Listings of an order

ListByOrder SHALL return every ResaleListing of the given Order's Tickets, in any status, oldest create time first, each with its status, price, provider refund ID and refund time. It SHALL return an empty list when there is none or no Order has the id.

#### Scenario: One ticket resold
- **WHEN** one of an Order's two Tickets was Sold through resale and its user refunded
- **THEN** that listing is returned with its refund time

#### Scenario: Never listed
- **WHEN** none of the Order's Tickets was listed
- **THEN** an empty list is returned
