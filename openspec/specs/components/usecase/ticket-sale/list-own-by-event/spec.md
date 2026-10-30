# components/usecase/ticket-sale/list-own-by-event Specification

## Purpose
TicketSaleUseCase.ListOwnByEvent shows an Organizer every sale of one of its events, with the entry stats of each TicketStock in each lottery sale, whether each lottery sale has been drawn, and the event's purchases per referral code.

## Requirements

### Requirement: The owner sees the event's sales with their entry stats per stock

ListOwnByEvent SHALL take the caller's Organizer, an event and the current time. It SHALL fail with PermissionDenied, without revealing whether the event exists, when Event.GetOrganizerID fails with NotFound or returns another Organizer. It SHALL list the event's sales with TicketSale.ListByEvent and its TicketStocks with TicketStock.ListByEvent, and return each sale, adding for a Lottery sale the entry stats of each TicketStock of the event from LotteryEntry.GetStatsByTicketSaleAndTicketStock, each with the TicketStock's id and SeatType. The stocks' quantities and their sold and held counts are not returned here; TicketStockUseCase.ListByEvent returns them. Beside them, it SHALL return the event's purchases per referral code from Order.ListReferralStatsByEvent, unchanged. It SHALL return no sale when the event has no sale, and an empty list of purchases per referral code when the event has no Paid Order.

#### Scenario: Drawn presale and upcoming general sale
- **WHEN** the owner reads an event with a drawn presale and a general sale that has not opened
- **THEN** both sales are returned in start order, the presale drawn with the entry, ticket, winner and loser counts of each TicketStock

#### Scenario: Event without a sale
- **WHEN** the owner reads an event that no sale names
- **THEN** no sale is returned

#### Scenario: Another Organizer's event
- **WHEN** a member reads the sales of another Organizer's event
- **THEN** ListOwnByEvent fails with PermissionDenied

#### Scenario: Purchases per referral code
- **WHEN** the owner reads an event whose Paid Orders include 12 with the code `member-a` and 40 without a code
- **THEN** the sales are returned together with `member-a` and the direct group, each with its Order count, ticket count and amount as Order.ListReferralStatsByEvent gives them
