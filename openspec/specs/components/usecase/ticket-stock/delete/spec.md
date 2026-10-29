# components/usecase/ticket-stock/delete Specification

## Purpose
TicketStockUseCase.Delete lets an Organizer remove a ticket stock it created by mistake, as long as no fan holds or is buying its tickets; a stock's quantity never changes, so a mistake is fixed by deleting and creating again.

## Requirements

### Requirement: Only a member of the owning Organizer deletes a stock no live Order names

Delete SHALL take the caller's Organizer and a TicketStock. It SHALL read the stock with TicketStock.Get, its event with Event.Get and the event's Series with Series.GetAuthored, and fail with PermissionDenied, without revealing whether it exists, when the stock does not exist or its Series is owned by another Organizer. It SHALL then delete it with TicketStock.Delete, which removes the stock with its Void Orders and fails with FailedPrecondition when an Order that is not Void names the stock; its failures are returned unchanged.

#### Scenario: Mistaken quantity before the sale
- **WHEN** a member deletes a TicketStock that no Order names, or only Void Orders of abandoned checkouts name
- **THEN** it is deleted

#### Scenario: Fans already applied
- **WHEN** a member deletes a TicketStock that a fan's Pending, Paid or Refunded Order names
- **THEN** Delete fails with FailedPrecondition and nothing changes

#### Scenario: Another Organizer's stock
- **WHEN** a member deletes a TicketStock of another Organizer's event
- **THEN** Delete fails with PermissionDenied and nothing changes
