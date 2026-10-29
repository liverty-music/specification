# Spec Delta

## Purpose

The fan screen where a signed-in fan applies for official resale (公式リセール) tickets of one seat type of a sold-out event and follows their resale entries: the next draw, and whether they won, lost or must apply again.

## ADDED Requirements

### Requirement: Applying for official resale

Opened for a TicketStock from the event page, the screen SHALL show the concert's title, date and venue, the seat type and its price 税込 (tax-inclusive), that tickets are allocated by a draw every day at 12:00 and on the event's day by 12:00 or 3 hours before the start time, whichever is earlier, that a group's tickets are allocated all together or not at all, and that the card is charged only when the fan wins. It SHALL let the fan choose a ticket count from 1 to the event's per-account limit minus the tickets they hold, confirm their full name and phone number, and authorize their card with ResaleEntryService.AuthorizeCard, then make the entry with ResaleEntryService.Confirm. After the entry is made it SHALL say 申し込みました (applied) and the time of the next draw. When the fan holds tickets of another seat type for the event, the screen SHALL say that one account can hold only one seat type and offer no application.

#### Scenario: Applying for two tickets
- **WHEN** a fan holding no ticket for the event chooses 2 tickets of S席 and authorizes their card
- **THEN** the screen says 申し込みました and the next draw time

#### Scenario: Another seat type held
- **WHEN** a fan holding A席 tickets opens the screen for S席
- **THEN** the screen says one account can hold only one seat type and offers no application

#### Scenario: Already applied
- **WHEN** a fan with an Entered entry for the event opens the screen
- **THEN** the screen shows that entry and its next draw and offers no second application

### Requirement: Following the fan's entries

The screen SHALL list the fan's resale entries from ResaleEntryService.List, newest first, each with the concert, the seat type, the ticket count and its state: 抽選待ち (waiting for the draw) with the next draw time, 当選 (won) with a link to the tickets screen, 落選 (lost), 期限切れ (lapsed) with the note that the card authorization expired before a ticket was found, that nothing was charged, and an action to apply again while resale is open, or 取り消し済み (withdrawn) with the note that nothing was charged and an action to apply again while resale is open. An entry waiting for the draw SHALL offer 申し込みを取り消す (withdraw the application); choosing it SHALL ask the fan to confirm that the application ends and nothing is charged, and confirming SHALL call ResaleEntryService.Withdraw. When the withdrawal is refused because a draw has already decided the entry, the screen SHALL say that the draw has already decided it and show the entry's new state.

#### Scenario: Lapsed entry
- **WHEN** a fan's entry lapsed and the event's resale is still open
- **THEN** the entry shows 期限切れ, says nothing was charged and offers to apply again

#### Scenario: Won entry
- **WHEN** a fan's entry won
- **THEN** it shows 当選 with a link to the tickets screen

#### Scenario: Withdrawing a waiting entry
- **WHEN** a fan chooses 申し込みを取り消す on a waiting entry and confirms
- **THEN** the entry shows 取り消し済み, says nothing was charged and offers to apply again

#### Scenario: Draw decided first
- **WHEN** a fan confirms the withdrawal just after the 12:00 draw made the entry win
- **THEN** the screen says the draw has already decided the entry and shows it as 当選
