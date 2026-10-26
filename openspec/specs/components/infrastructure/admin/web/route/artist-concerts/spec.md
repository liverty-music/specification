# components/infrastructure/admin/web/route/artist-concerts Specification

## Purpose
The admin console's Artist concerts screen, opened from an Organizer's roster, lists every Concert one Artist performs in. On it an admin refunds every fan of a cancelled Concert and deletes Concerts.

## Requirements

### Requirement: The screen lists the Artist's concerts with their orders

The Artist concerts screen SHALL be opened with the Artist's id only. It SHALL show the Artist's name, read with ArtistService.Get, and list the Concerts that ConcertService.ListByArtist returns for the Artist, oldest first. When ArtistService.Get fails with NotFound, the screen SHALL show `No artist has this id.` and no Concerts. Each row SHALL show:
- the Concert's date, its Series title and its venue;
- its state: `Published`, `Cancelled`, or `Discovered` for a Concert of a discovered Series;
- for an Organizer's Concert, the number of its Paid Orders and their total in yen, read with OrderService.ListByEvent.

An Artist with no Concert SHALL show its name and `No concerts.`

#### Scenario: Cancelled concert with paid orders

- **WHEN** the Artist performs in a CANCELLED Organizer Concert with two Paid Orders of 3,000 yen and 5,000 yen and one Refunded Order
- **THEN** its row shows `Cancelled`, 2 Paid Orders and 8,000 yen

#### Scenario: No concerts

- **WHEN** the Artist performs in no Concert
- **THEN** the screen shows the Artist's name and `No concerts.`

#### Scenario: Unknown artist

- **WHEN** the screen is opened with an id no Artist has
- **THEN** it shows `No artist has this id.` and no Concerts

### Requirement: Refund all refunds every paid order of a cancelled concert

A row SHALL offer `Refund all` only when the Concert is CANCELLED and has a Paid Order. Activating it SHALL open a modal confirmation dialog stating the number of Paid Orders and their total in yen and that each fan is refunded for 中止 (cancellation). Cancel SHALL receive initial focus, and Cancel and Escape SHALL close the dialog without refunding.

On confirmation the screen SHALL call OrderService.Refund with the reason Cancellation for each Paid Order, one at a time, showing how many are done. It SHALL stop at the first failure and show `Refunded <n> of <m> orders. Try again to refund the rest.` After every call it SHALL read the Orders again. A repeated `Refund all` refunds only the Orders still Paid.

#### Scenario: All refunded

- **WHEN** the admin confirms `Refund all` for a CANCELLED Concert with two Paid Orders and both refunds succeed
- **THEN** OrderService.Refund is called twice with the reason Cancellation, and the row shows 0 Paid Orders and no longer offers `Refund all`

#### Scenario: Refund stops part-way

- **WHEN** the first of three refunds succeeds and the second fails with Unavailable
- **THEN** the third is not attempted, the screen shows `Refunded 1 of 3 orders. Try again to refund the rest.`, and the row shows 2 Paid Orders

#### Scenario: Published concert

- **WHEN** a row's Concert is PUBLISHED and has Paid Orders
- **THEN** the row does not offer `Refund all`

#### Scenario: Dismissed

- **WHEN** the admin activates `Refund all` and then presses Escape
- **THEN** the dialog closes and OrderService.Refund is not called

### Requirement: Delete removes a concert after confirmation

Every row SHALL offer `Delete`. Activating it SHALL open a modal confirmation dialog that names the Concert by date and Series title and says that the Concert and its records are removed permanently. Cancel SHALL receive initial focus, and Cancel and Escape SHALL close the dialog without deleting. ConcertService.Delete SHALL be called only when the admin activates the dialog's Delete control, which SHALL be disabled while the call is in flight. When Delete succeeds the row SHALL leave the list. When it fails with FailedPrecondition the screen SHALL keep the row and show `This concert cannot be deleted while it has a paid order, a settlement that is not reversed, or a purchase in progress.`, whatever reason the server gives. Any other failure SHALL show `Failed to delete the concert.` with the row kept.

#### Scenario: Refunded cancelled concert deleted

- **WHEN** the admin deletes a CANCELLED Concert whose Orders are all Refunded and confirms
- **THEN** ConcertService.Delete is called once and the row leaves the list

#### Scenario: Delete blocked by a paid order

- **WHEN** Delete fails with FailedPrecondition because the Concert has a Paid Order
- **THEN** the row stays and the screen shows `This concert cannot be deleted while it has a paid order, a settlement that is not reversed, or a purchase in progress.`

#### Scenario: Delete dismissed

- **WHEN** the admin activates Delete and then Cancel
- **THEN** the dialog closes and ConcertService.Delete is not called
