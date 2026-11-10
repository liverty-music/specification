# stories/remove-a-cancelled-concert Specification

## Purpose
An Organizer's Concert is called off: a member cancels its Event, then an admin refunds every fan who bought a ticket and, when the Event should no longer exist at all, deletes it from the admin console. Test Events of a test Organizer are retired the same way.

```mermaid
eventmodeling
tf 01 ui Member_Event
tf 02 cmd SeriesUseCase_Cancel
tf 03 evt Event_Cancelled
tf 04 cmd NotificationUseCase_SendEventCancelled
rf 05 cmd LotteryEntryUseCase_EndForCancelledEvent ->> 03
tf 06 evt LotteryEntry_Drawn
tf 07 cmd OrderUseCase_ReleaseCardAuthorization
rf 08 rmo ArtistUseCase_Get
tf 09 rmo ConcertUseCase_ListCatalogByArtist
tf 10 rmo OrderUseCase_ListByEvent
tf 11 ui Admin_ArtistConcerts
tf 12 cmd OrderUseCase_Refund
tf 13 evt Order_Refunded
tf 14 cmd NotificationUseCase_SendOrderRefunded
rf 15 cmd ConcertUseCase_Delete ->> 11
```

## Requirements

### Requirement: A cancelled concert is refunded and then removed

After a member cancels an Event with SeriesUseCase.Cancel, an admin SHALL be able to refund every Paid Order of that Event for 中止 (cancellation) with `Refund all` on the Artist concerts screen, and then delete the Event with `Delete`. The deletion SHALL remove the Event with its refunded purchases and, when it was the Series' last Event, the Series. Before the Event is cancelled, neither a 中止 refund nor, while a Paid Order remains, the deletion SHALL succeed.

#### Scenario: Cancelled, refunded and deleted

- **WHEN** a member cancels the only Event of a Series with two Paid Orders, and an admin uses `Refund all` and then `Delete` on the Artist concerts screen
- **THEN** both fans' Orders are Refunded with their Tickets Voided, the Event and the Series no longer exist, and the Event's page is not found

#### Scenario: Refund before cancellation

- **WHEN** an admin refunds a Paid Order for 中止 while its Event is still PUBLISHED
- **THEN** the refund fails, no money moves and the Artist concerts screen does not offer `Refund all` for that Event

#### Scenario: Delete before refunds

- **WHEN** an admin deletes a CANCELLED Event that still has a Paid Order
- **THEN** the deletion fails and the Event and its Orders remain

### Requirement: Each fan with a Paid Order is told of the cancellation and of the refund

When a member cancels an Event with SeriesUseCase.Cancel, each fan with a Paid Order of it that still holds an Issued Ticket SHALL receive a cancellation email and push saying the concert is 中止 (cancelled) and its tickets are refunded. When an admin then refunds the Order for 中止, that fan SHALL receive a refund email and push with the amount and the card it went to. A fan whose every Ticket of the Order was resold through official resale (公式リセール) receives neither, since nothing of the Order is refunded. Each fan SHALL receive each notice once per Order.

#### Scenario: Cancelled and refunded
- **WHEN** a member cancels an Event with two Paid Orders of two fans, and an admin uses `Refund all` on the Artist concerts screen
- **THEN** each fan receives one cancellation email and push, then one refund email and push with their amount

#### Scenario: Deleted right after the refunds
- **WHEN** an admin uses `Delete` after `Refund all` and the refund notices were already sent
- **THEN** each fan still has the refund email, and the Event no longer exists

### Requirement: An open lottery does not hold up the removal

A lottery entry that is Entered when an Event's cancellation is announced SHALL end soon after it, so that its Void Order no longer blocks the deletion of the Event, even while the sale's window is still open.

#### Scenario: Deleted during the window
- **WHEN** a member cancels the only Event of a Series whose lottery window is open, with one fan Entered and no Paid Order, and an admin uses `Delete` on the Artist concerts screen after the entry has ended
- **THEN** the Event, the Series, the entry and its Void Order no longer exist
