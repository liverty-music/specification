# Spec Delta

## Purpose

ResaleEntryUseCase.Draw runs the official resale draws due at a time: for each TicketStock whose event has a draw at that time, it allocates the free listings to the Entered entries in random order, ends the entries that lapse or, at the last draw, lose, and records the outcome; the winners are charged from its announcement.

## ADDED Requirements

### Requirement: Draw every stock due at a time

Draw SHALL run on a schedule every minute with the scheduled time. For every TicketStock whose event has a draw at that time ("Draw times of an event") and that has Entered entries, it SHALL draw that stock on its own, so a stock whose draw fails does not stop the draws of the other stocks at that time, and a stock is drawn at most once for a scheduled time. For each stock it SHALL:
- list the candidates with ResaleEntry.ListEnteredByTicketStock;
- end as lapsing every candidate that does not take part in the draw ("Taking part in a draw");
- read the listings free for a draw at that time, oldest first, and go through the other candidates in a random order, giving each, all-or-nothing, as many listings as its ticket count while enough remain;
- at the last draw of the event, end as losing every candidate that won nothing, with the lost reason "no ticket left";
- record the outcome with ResaleEntry.PersistDrawOutcome.
Draw SHALL start no other work itself: ResaleEntry.PersistDrawOutcome announces each entry it records, and the work that follows runs from that announcement: OrderUseCase.Issue for each Won entry's Order, and for each Lapsed or Lost entry OrderUseCase.ReleaseCardAuthorization for its Order and NotificationUseCase.SendResaleEntryEnded. When the event of a TicketStock with Entered entries is no longer PUBLISHED at a scheduled draw time of that stock, as for a 中止 (cancelled) concert, Draw SHALL allocate nothing and end every candidate as losing, as at the last draw, with the lost reason "concert cancelled".

#### Scenario: More applications than listings
- **WHEN** at 12:00 a stock has 3 free listings and Entered entries for 2, 2 and 1 tickets, all with card authorizations valid for a week
- **THEN** the entries are taken in a random order and the listings go to entries that fit, for example the first entry for 2 and the entry for 1, while the other entry for 2 stays Entered

#### Scenario: Card authorization about to lapse
- **WHEN** at 12:00 an Entered entry's card authorization expires at 09:00 the next day
- **THEN** the entry is Lapsed, its Order Void, its card authorization released and the fan told to apply again

#### Scenario: Last draw
- **WHEN** the event's last draw allocates every free listing and an entry for 2 tickets gets none
- **THEN** that entry is Lost, its Order Void, its card authorization released and the fan told the result

#### Scenario: No listing yet
- **WHEN** a draw that is not the last finds no free listing
- **THEN** every candidate whose card authorization stays valid stays Entered

#### Scenario: Concert cancelled
- **WHEN** at 12:00 the event of a stock with Entered entries is CANCELLED
- **THEN** every entry is Lost with its Order Void, its card authorization released and the fan told, and no listing is allocated
