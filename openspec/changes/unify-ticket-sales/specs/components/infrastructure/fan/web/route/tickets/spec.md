# Spec Delta

## MODIFIED Requirements

### Requirement: Tickets grouped by event with their face

The screen SHALL list the signed-in fan's tickets grouped by event, nearest event first. Each ticket SHALL show its event's title, date, venue, open and start times, and its covered-ticket face: that resale without the organizer's consent is prohibited, the eligible person's full name and phone number as the fan's User currently records them, and that no seat is assigned. Each ticket SHALL show its state: 未入場 (not yet entered), 入場済み (entered) with the admit time, or 無効 (void). The last loaded list SHALL stay viewable without a connection.

#### Scenario: Fan opens their tickets

- **WHEN** a fan with 3 tickets for one event opens the screen
- **THEN** the event is shown once with its 3 tickets, each with the resale notice, the fan's full name and phone number and 未入場

#### Scenario: Fan corrected their phone number

- **WHEN** the fan changed their phone number after the tickets were issued and opens the screen with a connection
- **THEN** each ticket's face shows the new phone number

#### Scenario: Refunded ticket

- **WHEN** one of the fan's tickets was voided by a refund
- **THEN** it is shown as 無効 and offers no QR code

#### Scenario: No signal in the venue

- **WHEN** the fan opens the screen without a connection after loading it earlier
- **THEN** the tickets loaded earlier are shown
