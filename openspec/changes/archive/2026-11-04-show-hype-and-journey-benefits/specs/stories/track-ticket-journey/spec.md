## MODIFIED Requirements

### Requirement: Guests and signed-out fans see no statuses

A guest SHALL have no ticket journey statuses, and the app SHALL not ask the server for any. A guest's event detail sheet SHALL offer only the ticket sale notification button, which starts sign-up. After a fan signs out, no screen SHALL show that fan's statuses.

#### Scenario: A guest opens the Dashboard

- **WHEN** a guest opens the Dashboard
- **THEN** no concert shows a journey status and no journeys are requested from the server

#### Scenario: A guest opens a concert

- **WHEN** a guest opens a concert's detail sheet
- **THEN** the sheet offers 「🔔 チケット販売の通知を受け取る」 and no other status

#### Scenario: Signing out clears the statuses

- **WHEN** a fan with journey statuses signs out and the next visitor opens the Dashboard in the same browser
- **THEN** none of the previous fan's statuses are shown

## ADDED Requirements

### Requirement: A guest's request for ticket sale notifications survives sign-up

When a guest presses the ticket sale notification button on a concert's detail sheet, signs up and the account is resolved, the app SHALL set Tracking for that event through TicketJourneyUseCase.SetStatus, as the fan's own choice, and SHALL open that concert's detail sheet. The Dashboard SHALL then show the event with the Tracking badge, and the fan SHALL receive the ticket sale reminders of the series like any tracking fan. When the guest leaves sign-up without finishing it, nothing SHALL be set, and a later sign-up started elsewhere SHALL NOT track the event.

#### Scenario: Guest signs up from the notification button

- **WHEN** a guest presses 「🔔 チケット販売の通知を受け取る」 on ヨルシカ's 20 December concert and completes sign-up
- **THEN** the fan's journey for that event is Tracking, the concert's detail sheet is open, and its card on the Dashboard shows 🔔

#### Scenario: Sign-up abandoned

- **WHEN** a guest presses the button, leaves hosted login without signing up, and later signs up from the Dashboard banner
- **THEN** the fan has no journey for that event
