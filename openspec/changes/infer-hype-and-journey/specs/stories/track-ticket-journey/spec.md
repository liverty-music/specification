## ADDED Requirements

### Requirement: Adding a concert to the calendar starts tracking it

When a signed-in fan with no journey for an event adds its concert to their calendar from the event detail sheet, TicketJourneyUseCase.InferTracking SHALL record Tracking for the event as an inference, every screen SHALL show Tracking for it, and the fan SHALL be able to undo it from the snack shown when they come back to the app. A journey the fan or the platform already recorded SHALL never be changed by a calendar add. A calendar add SHALL be the only action the app records Tracking from; opening a notification or a detail sheet SHALL record no journey.

#### Scenario: Calendar add starts tracking and the fan hears about the sale

- **WHEN** a signed-in fan with no journey for an event adds it to their calendar, and later a ticket sale for the event's series is found that has not opened
- **THEN** the fan's journey for the event is Tracking, and the fan is told about the sale as for any Tracking journey

#### Scenario: Undo removes the inferred journey

- **WHEN** the fan presses 「取り消す」 on the snack after coming back from the calendar
- **THEN** the event has no journey on any screen

#### Scenario: Existing journey kept

- **WHEN** a fan whose journey for the event is Paid adds it to their calendar
- **THEN** the journey stays Paid

#### Scenario: Opening a new-concert push changes no journey

- **WHEN** the fan opens a new-concert push notification and the detail sheet of the earliest concert opens
- **THEN** no journey is recorded for any concert in the notification

### Requirement: A journey for a distant concert raises the artist's hype level

When a signed-in fan saves Applied, Unpaid or Paid for a concert in the event detail sheet, and the fan follows exactly one of its artists at a hype level the fan did not set that does not match the concert, TicketJourneyUseCase.SetStatus SHALL raise that hype level to the lowest level that matches the concert. My Artists and the Dashboard SHALL show the new level, and the sheet SHALL offer to undo it.

#### Scenario: Applied for a distant concert

- **WHEN** a signed-in fan with home JP-13 who never set ヨルシカ's hype level saves Applied for ヨルシカ's concert in JP-40
- **THEN** My Artists shows ヨルシカ at Away and the JP-40 concert is highlighted on the Dashboard
