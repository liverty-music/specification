# components/infrastructure/fan/web/route/resale-entries Specification

## Purpose
The fan screen that lists the fan's official resale (公式リセール) entries across events: the next draw, whether each entry won, lost, lapsed or was withdrawn, and the actions to withdraw a waiting entry or apply again.

## Requirements

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
