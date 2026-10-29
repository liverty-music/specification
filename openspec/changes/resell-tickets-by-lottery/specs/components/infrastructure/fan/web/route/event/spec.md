# Spec Delta

## ADDED Requirements

### Requirement: Official resale by lottery in the ticket section

When a TicketStock of the Event is SoldOut and its resale is open, the ticket section SHALL show, for that stock, 公式リセール (official resale): that tickets listed by fans who cannot attend are allocated at face value by a daily draw, and an action 公式リセールに申し込む (apply for official resale) that opens the resale entry screen for the stock. It SHALL never show how many tickets are listed or how many fans applied. When the fan already has an Entered resale entry for the Event, the action SHALL instead show 申し込み済み (applied) and open the resale entry screen.

#### Scenario: Sold out, resale open
- **WHEN** a guest opens the page of an event whose S席 stock is sold out and whose resale is open
- **THEN** the ticket section shows 公式リセール for S席 with the action 公式リセールに申し込む and no count

#### Scenario: Already applied
- **WHEN** a fan with an Entered resale entry for the event opens the page
- **THEN** the section shows 申し込み済み
