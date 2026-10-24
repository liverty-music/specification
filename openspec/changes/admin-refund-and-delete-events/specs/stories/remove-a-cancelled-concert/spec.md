## Purpose

An Organizer's Concert is called off: a member cancels its Event, then an admin refunds every fan who bought a ticket and, when the Event should no longer exist at all, deletes it from the admin console. Test Events of a test Organizer are retired the same way.

```mermaid
usecase-beta
direction LR
actor Admin("admin")
actor Member("member")
systemBoundary "Liverty Music"
  Goal("Remove a cancelled concert")
  SeriesUseCaseCancel("SeriesUseCase.Cancel")
  ConcertUseCaseList("ConcertUseCase.List")
  OrderUseCaseListByEvent("OrderUseCase.ListByEvent")
  OrderUseCaseRefund("OrderUseCase.Refund")
  ConcertUseCaseDelete("ConcertUseCase.Delete")
end
Admin --> Goal
Goal ..> : include SeriesUseCaseCancel
Goal ..> : include ConcertUseCaseList
Goal ..> : include OrderUseCaseListByEvent
Goal ..> : include OrderUseCaseRefund
Goal ..> : include ConcertUseCaseDelete
Member --> SeriesUseCaseCancel
```

## ADDED Requirements

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
