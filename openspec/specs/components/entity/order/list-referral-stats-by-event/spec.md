# components/entity/order/list-referral-stats-by-event Specification

## Purpose
Order.ListReferralStatsByEvent counts the Paid Orders of one event per referral code, with the purchases that have no code as one direct group, for the Organizer's view of which links sold the event's tickets.

## Requirements

### Requirement: Paid Orders of an event per referral code

ListReferralStatsByEvent SHALL take an event and consider every Order whose status is Paid and whose TicketStock is of that event. It SHALL group those Orders by their referral code, putting the Orders without a referral code into one direct group without a code. For each group that has at least one Order it SHALL return:
- the code, absent for the direct group;
- the number of Orders;
- the number of tickets: the sum of the Orders' ticket counts;
- the amount: the sum of the Orders' amounts, in whole yen.

Pending, Void and Refunded Orders SHALL NOT be counted, so a lottery entry counts only once it won and its Order became Paid. Groups SHALL be ordered by the number of Orders, most first, then by code. An event with no Paid Order, or an event that does not exist, SHALL yield an empty list.

#### Scenario: Two codes and direct purchases
- **WHEN** an event has Paid Orders of 2 and 3 tickets for 6,500 and 9,750 yen with the code `member-a`, and one Paid Order of 1 ticket for 3,250 yen without a code
- **THEN** the list is `member-a` with 2 Orders, 5 tickets and 16,250 yen, then the direct group with 1 Order, 1 ticket and 3,250 yen

#### Scenario: Lottery win counted once its Order exists
- **WHEN** a Pending Order of an Entered LotteryEntry for the event has the code `member-b`
- **THEN** `member-b` is not in the list, and after the entry won and its Order of 2 tickets for 16,000 yen became Paid, `member-b` has 1 Order, 2 tickets and 16,000 yen

#### Scenario: Refunded order excluded
- **WHEN** the only Order with the code `member-a` is Refunded
- **THEN** `member-a` is not in the list

#### Scenario: Abandoned checkout not counted
- **WHEN** an Order with the code `member-c` became Void when its Checkout expired
- **THEN** `member-c` is not in the list

#### Scenario: Other events not counted
- **WHEN** a Paid Order's TicketStock is of another event of the same Series
- **THEN** it is not counted for this event

#### Scenario: No purchases
- **WHEN** the event has no Paid Order
- **THEN** the list is empty
