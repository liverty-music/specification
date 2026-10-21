# components/entity/resale-listing/list-by-user Specification

## Purpose
Lists the ResaleListings one fan has made, so the fan can see what they offered and what was refunded.

## Requirements

### Requirement: A fan's listings, newest first

ListByUser SHALL return every ResaleListing whose user is the given User, in every status, newest create time first, and an empty list when there are none.

#### Scenario: Two listings
- **WHEN** the User listed one Ticket on 1 November, withdrew it, and listed another on 3 November
- **THEN** both listings are returned, the 3 November listing first

#### Scenario: No listings
- **WHEN** the User never listed a Ticket
- **THEN** an empty list is returned
