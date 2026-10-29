# Spec Delta

## Purpose

NotificationUseCase.SendResaleEntryEnded tells a fan, by email and push notification, that their official resale (公式リセール) entry lapsed because its card authorization would expire, or ended without a ticket: it lost at the event's last draw, its concert was cancelled, it won but its card could not be charged, or it won but the payment could not be completed before the show.

## ADDED Requirements

### Requirement: Lapse and loss messages

SendResaleEntryEnded SHALL run for each ResaleEntry that became Lapsed or Lost. It SHALL read the entry with ResaleEntry.Get, its user with User.Get and the event's concert with Concert.ListByIDs, then:
- send, with ResaleEntry.SendEndedEmail, in the user's preferred language (Japanese when none), a message naming the concert's title, date, venue and seat type and, for a Lapsed entry, that the card authorization for the application expired before a resale ticket was found, that nothing was charged and that the fan can apply again while resale is open, with a link to the resale entry screen; for a Lost entry, by its lost reason, that no resale ticket was left at the last draw, that the concert was cancelled, that the entry won but the card could not be charged so the win was cancelled, or that the entry won but the payment could not be completed before the show because of a problem at the payment provider, and that nothing was charged. For a win cancelled because the card could not be charged, while resale of the event is still open (before its resale deadline) the message SHALL also invite the fan to apply again with another card, with a link to the resale entry screen; after the deadline it SHALL say resale for the event has closed;
- start NotificationUseCase.Deliver for the user with a notification of type `resale_entry_lapsed` or `resale_entry_lost`, named after the type and the entry, with the same message in short, opening the resale entry screen; a run again for the same entry starts no second push.
When reading or sending fails, it SHALL fail with that error and is run again; ResaleEntry.SendEndedEmail keeps it to one email per entry.

#### Scenario: Lapsed entry
- **WHEN** a fan's entry for 2 S席 lapses
- **THEN** the fan receives one email and one `resale_entry_lapsed` push saying nothing was charged and inviting them to apply again

#### Scenario: Lost at the last draw
- **WHEN** a fan's entry is Lost at the last draw
- **THEN** the fan receives one email and one `resale_entry_lost` push saying no ticket was allocated and nothing was charged

#### Scenario: Run again after the email was sent
- **WHEN** SendResaleEntryEnded runs again for the same entry after its email was sent
- **THEN** no second email is sent

#### Scenario: Won but not charged while resale is open
- **WHEN** a fan's entry won at 12:00 two days before the event and became Lost with the lost reason "card could not be charged"
- **THEN** the fan receives one email and one `resale_entry_lost` push saying the win was cancelled because the card could not be charged, that nothing was charged, and inviting them to apply again with another card, with a link to the resale entry screen

#### Scenario: Won but not charged after resale closed
- **WHEN** a fan's entry became Lost with the lost reason "card could not be charged" after the event's resale deadline
- **THEN** the message says the win was cancelled, nothing was charged and resale for the event has closed, with no invitation to apply again

#### Scenario: Concert cancelled
- **WHEN** a fan's entry is Lost with the lost reason "concert cancelled"
- **THEN** the fan receives one email and one `resale_entry_lost` push saying the concert was cancelled and nothing was charged

#### Scenario: Payment not completed before the show
- **WHEN** a fan's entry is Lost with the lost reason "payment not completed before the show"
- **THEN** the fan receives one email and one `resale_entry_lost` push saying the entry won but the payment could not be completed before the show because of a problem at the payment provider, that nothing was charged, and that resale for the event has closed
