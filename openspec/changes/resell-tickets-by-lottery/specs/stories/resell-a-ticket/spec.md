# Spec Delta

## ADDED Requirements

### Requirement: A ticket is resold and its fan refunded

After a TicketStock sold out, a signed-in fan holding Issued Tickets of it SHALL be able to list one with ResaleListingUseCase.Create. Another signed-in fan SHALL be able to apply for resale tickets of the stock with ResaleEntryUseCase.AuthorizeCard and ResaleEntryUseCase.Confirm. At the next daily draw (ResaleEntryUseCase.Draw) the listing SHALL be allocated to an applying fan whose ticket count fits, and OrderUseCase.Issue SHALL charge that fan. The first fan's listed Ticket SHALL then be Voided, the other fan SHALL hold a new Issued Ticket for the event in TicketUseCase.List and receive the purchase confirmation email, and within 2 minutes of the charge the first fan SHALL be refunded the refund amount and receive the sold email.

#### Scenario: One of two tickets resold
- **WHEN** a fan holding 2 tickets of 5000 yen for a sold-out stock lists one, another fan applies for 1 ticket, and the 12:00 draw runs
- **THEN** the other fan is charged 5000 yen and holds 1 Issued Ticket, the first fan holds 1 Issued and 1 Voided Ticket, is refunded 4500 yen within 2 minutes and receives one sold email, and ResaleListingUseCase.List shows the listing Sold and refunded

### Requirement: Nobody gets a seat twice and nobody is charged without a ticket

A listing SHALL be allocated to at most one entry at a time and sold to at most one fan. A fan whose entry does not win SHALL NOT be charged and SHALL have their card authorization released. A listing withdrawn before a draw allocates it SHALL NOT be sold.

#### Scenario: Two fans, one listing
- **WHEN** one listing is free and two fans have each applied for 1 ticket before the 12:00 draw
- **THEN** the draw allocates it to one of them, who is charged, and the other stays waiting for the next draw and is not charged

#### Scenario: Withdrawn before the draw
- **WHEN** the listing fan withdraws before the 12:00 draw
- **THEN** the draw allocates nothing from that listing and the fan's Ticket is 未入場 (not yet entered)

#### Scenario: Nobody wins at the last draw
- **WHEN** at the event's last draw a fan's entry for 2 tickets finds only 1 free listing
- **THEN** the fan is not charged, their card authorization is released and they receive the loss email and push

### Requirement: A lapsed application is told to apply again

A fan whose resale entry lapses because its card authorization would expire before it could be charged SHALL NOT be charged, SHALL have the card authorization released, and SHALL receive an email and a push notification inviting them to apply again; applying again SHALL be possible while resale is open.

#### Scenario: Authorization about to expire
- **WHEN** a fan's entry still waits at the draw before its card authorization expires
- **THEN** the entry lapses at that draw, the fan is told by email and push, and the fan can apply again from the resale entry screen

### Requirement: A fan can withdraw a waiting application

A fan whose resale entry is still waiting for a draw SHALL be able to withdraw it; they SHALL NOT be charged, their card authorization SHALL be released, and no later draw SHALL allocate them a ticket.

#### Scenario: Plans changed
- **WHEN** a fan applied for 2 tickets and withdraws the application before the 12:00 draw
- **THEN** the 12:00 draw allocates them nothing, they are not charged, and the hold on their card is released

### Requirement: The Organizer is paid once per seat

A resale SHALL leave the Organizer's total payout for the event as it was before, to within 1 yen per resold ticket from rounding.

#### Scenario: Payout after a resale
- **WHEN** an Organizer at a 5% rate sold 2 tickets of 5000 yen to one fan and one of them was resold through a resale draw
- **THEN** the Held Settlements of the two Orders together pay the Organizer 9500 yen

### Requirement: Resale ends when the event is cancelled

A fan waiting for a resale draw of an event that is cancelled (中止) SHALL NOT be charged, SHALL have their card authorization released and SHALL be told the application ended.

#### Scenario: Cancelled before the draw
- **WHEN** a fan's entry waits for a draw and the concert is cancelled
- **THEN** at the next draw time the entry is Lost, nothing is charged, the hold on the card is released and the fan is told
