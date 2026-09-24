# Track ticket journey

## Purpose

A fan records where they stand in getting a ticket for an event and sees the same status for that event on every screen, right after the change is saved and never from someone else's session.

## Requirements

### Requirement: One status per event on every screen

A fan's ticket journey status for an event SHALL be the same on the Dashboard and in the event detail sheet. A status the fan sets or removes in the event detail sheet SHALL appear on the Dashboard as soon as the server accepts it, without the fan reloading or leaving the Dashboard.

#### Scenario: Setting a status in the detail sheet updates the Dashboard

- **WHEN** a signed-in fan sets Applied for an event in the event detail sheet and the change is saved
- **THEN** the event detail sheet and the Dashboard's card for that event both show Applied, without the fan leaving or reloading the Dashboard

#### Scenario: Removing a status in the detail sheet updates the Dashboard

- **WHEN** a signed-in fan removes their journey for an event in the event detail sheet and the removal is saved
- **THEN** neither the event detail sheet nor the Dashboard shows a status for that event

#### Scenario: Both screens agree

- **WHEN** the Dashboard and the event detail sheet both show the same event
- **THEN** they show the same journey status for it

### Requirement: A status is shown only after the server accepts it

A status change SHALL appear on the fan's screens only after the server has saved it. When saving fails, every screen SHALL keep showing the status the fan had before.

#### Scenario: Saving fails

- **WHEN** a signed-in fan picks Paid for an event whose status is Unpaid and saving fails
- **THEN** the Dashboard and the event detail sheet still show Unpaid

### Requirement: Statuses are loaded fresh and never overwrite a newer change

Each time the Dashboard loads its concerts for a signed-in fan, it SHALL show the fan's latest journey statuses from the server. A status the fan saved while that load was still running SHALL NOT be replaced by the older loaded status.

#### Scenario: Opening the Dashboard shows the latest statuses

- **WHEN** a signed-in fan changed a journey status on another device and then opens the Dashboard
- **THEN** the Dashboard shows the status saved on the other device

#### Scenario: A change saved during a load wins

- **WHEN** the Dashboard is loading statuses and the fan saves Unpaid for an event before the load finishes
- **THEN** the event keeps showing Unpaid after the load finishes

### Requirement: Guests and signed-out fans see no statuses

A guest SHALL have no ticket journey statuses, and the app SHALL not ask the server for any. After a fan signs out, no screen SHALL show that fan's statuses.

#### Scenario: A guest opens the Dashboard

- **WHEN** a guest opens the Dashboard
- **THEN** no concert shows a journey status and no journeys are requested from the server

#### Scenario: Signing out clears the statuses

- **WHEN** a fan with journey statuses signs out and the next visitor opens the Dashboard in the same browser
- **THEN** none of the previous fan's statuses are shown
