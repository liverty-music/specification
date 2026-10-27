## MODIFIED Requirements

### Requirement: The owner sees the event's sales with their entry stats

ListOwnByEvent SHALL take the caller's Organizer, an event and the current time. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL list the event's sales with TicketSale.ListByEvent and return each sale with its TicketTypes, adding for each TicketType of a Lottery sale the entry stats from LotteryEntry.GetStatsByTicketType, and for each TicketType of a FirstCome sale its quantity, sold count, and held count and state at that time. Beside the sales, it SHALL return the event's purchases per referral code from Order.ListReferralStatsByEvent, unchanged. It SHALL return an empty list of sales when the event has no sale, and an empty list of purchases per referral code when the event has no Paid Order.

#### Scenario: Drawn presale and upcoming general sale
- **WHEN** the owner reads an event with a drawn presale and a general sale that has not opened
- **THEN** both sales are returned in start order, the presale drawn with its entry, ticket, winner and loser counts

#### Scenario: Owner checks first-come sales
- **WHEN** the owner reads an event whose first-come TicketType of 150 has 100 sold and 6 held
- **THEN** the sale is returned with that TicketType's quantity 150, 100 sold and 6 held

#### Scenario: Event without a sale
- **WHEN** the owner reads an event that no sale offers
- **THEN** an empty list is returned

#### Scenario: Another Organizer's event
- **WHEN** a member reads the sales of another Organizer's event
- **THEN** ListOwnByEvent fails with PermissionDenied

#### Scenario: Purchases per referral code
- **WHEN** the owner reads an event whose Paid Orders include 12 from Checkouts with the code `member-a` and 40 without a code
- **THEN** the sales are returned together with `member-a` and the direct group, each with its Order count, ticket count and amount as Order.ListReferralStatsByEvent gives them
