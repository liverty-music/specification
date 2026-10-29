# Spec Delta

## Purpose

NotificationUseCase.SendResaleEntryEnded tells a fan, by email and push notification, that their official resale (公式リセール) entry lapsed because its card authorization would expire, or ended without a ticket: it lost at the event's last draw, its concert was cancelled, or it won but its card could not be charged.

## ADDED Requirements

### Requirement: Lapse and loss messages

SendResaleEntryEnded SHALL run for each ResaleEntry that became Lapsed or Lost. It SHALL read the entry with ResaleEntry.Get, its user with User.Get and the event's concert with Concert.ListByIDs, then:
- send, with ResaleEntry.SendEndedEmail, in the user's preferred language (Japanese when none), a message naming the concert's title, date, venue and seat type and, for a Lapsed entry, that the card authorization for the application expired before a resale ticket was found, that nothing was charged and that the fan can apply again while resale is open, with a link to the resale entry screen; for a Lost entry, that no resale ticket could be given to the fan (none was left at the last draw, the concert was cancelled, or the card could not be charged after the draw) and that nothing was charged;
- deliver a push notification of type `resale_entry_lapsed` or `resale_entry_lost` with the same message in short, opening the resale entry screen.
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

#### Scenario: Won but not charged
- **WHEN** a fan's entry won at 12:00 and became Lost because the card could no longer be charged
- **THEN** the fan receives one email and one `resale_entry_lost` push saying no ticket could be given and nothing was charged
