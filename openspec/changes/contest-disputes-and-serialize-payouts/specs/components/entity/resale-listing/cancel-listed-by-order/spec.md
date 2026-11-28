# Spec Delta

## Purpose

Withdraws from official resale every listing of one Order's Tickets that is Listed and not being bought, so the Order's Tickets stop being offered.

## ADDED Requirements

### Requirement: Listed listings of an order cancelled

CancelListedByOrder SHALL set to Cancelled, together or not at all, every Listed ResaleListing of the given Order's Tickets that is not allocated to a Won ResaleEntry, and return how many it cancelled. A listing allocated to a Won ResaleEntry, whose fan is being charged for it, and a Sold, Withdrawn or Cancelled listing, SHALL stay as it is; a listing still allocated to an entry that Lost or Lapsed is cancelled. It SHALL return 0 when there is nothing to cancel or no Order has the id.

#### Scenario: Two tickets listed
- **WHEN** an Order has two Tickets Listed for resale and neither is allocated
- **THEN** both listings are Cancelled and 2 is returned

#### Scenario: Entry being charged
- **WHEN** an Order's only Listed listing is allocated to a Won ResaleEntry
- **THEN** it stays Listed and 0 is returned

#### Scenario: Entry's charge failed
- **WHEN** an Order's only Listed listing is allocated to a ResaleEntry that Lapsed
- **THEN** the listing is Cancelled and 1 is returned

#### Scenario: Nothing listed
- **WHEN** none of the Order's Tickets is Listed
- **THEN** nothing changes and 0 is returned
