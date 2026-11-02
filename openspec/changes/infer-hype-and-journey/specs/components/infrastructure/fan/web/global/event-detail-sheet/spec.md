## ADDED Requirements

### Requirement: Adding to the calendar starts tracking

When a signed-in fan with no journey for the event chooses add to calendar in the event detail sheet, the app SHALL start tracking the event as an inference (TicketJourneyService.InferTracking) at once, and every screen SHALL show Tracking for the event once it is saved. When the fan comes back to the app after the calendar opened, or at once when the app stayed in view, the sheet SHALL show a snack that reads 「チケット状況を「追跡中」にしました。」 and 「販売の情報をお知らせします。」 on two lines (EN "Ticket status set to Tracking." / "We will tell you about ticket sales."), with the action 「取り消す」 (EN "Undo"). The snack SHALL stay 10 seconds unless the fan presses the action. Pressing it SHALL remove the journey, and no screen SHALL then show a status for the event. A guest's calendar add, a fan who already has a journey for the event, and a save that fails SHALL start nothing and show no snack.

#### Scenario: Calendar add from the sheet

- **WHEN** a signed-in fan with no journey for an event chooses add to calendar, the calendar opens, and the fan comes back to the app
- **THEN** the sheet and the Dashboard show Tracking for the event and the snack offers 「取り消す」

#### Scenario: Undo

- **WHEN** the fan presses 「取り消す」 on that snack
- **THEN** neither the sheet nor the Dashboard shows a status for the event

#### Scenario: Fan already has a journey

- **WHEN** a signed-in fan whose journey for the event is Applied chooses add to calendar
- **THEN** the journey stays Applied and no snack appears

#### Scenario: Guest

- **WHEN** a guest chooses add to calendar
- **THEN** the calendar opens, no journey is requested from the server and no snack appears

### Requirement: A hype level raised by a journey change is shown with undo

When a signed-in fan's Applied, Unpaid or Paid in the event detail sheet is saved and the app raised the fan's hype level for the concert's artist as a result, the sheet SHALL show a snack that reads 「{{name}}を {{hype}} にしました。」 and 「遠方の新着ライブも通知します。」 on two lines (EN "{{name}} is now {{hype}}." / "You will also hear about distant new concerts."), where `{{hype}}` is the invariant English tier label, with the action 「取り消す」 (EN "Undo"), and the Dashboard SHALL highlight the artist's concerts the new level matches. The snack SHALL stay 10 seconds unless the fan presses the action. Pressing it SHALL set the previous level as the fan's own choice; when that save fails, the raised level stays shown and a message says the change failed. When the level was not raised, no snack SHALL appear.

#### Scenario: Applied for a distant concert raises the level

- **WHEN** a signed-in fan whose hype for ヨルシカ is Nearby set by default saves Applied for ヨルシカ's concert in the away lane
- **THEN** the snack reads 「ヨルシカを Away にしました。」 「遠方の新着ライブも通知します。」 and the concert's card on the Dashboard is highlighted

#### Scenario: Undo the raise

- **WHEN** the fan presses 「取り消す」 on that snack
- **THEN** ヨルシカ is at Nearby, set by the fan, and the away-lane card is no longer highlighted

#### Scenario: Level not raised

- **WHEN** the fan's hype for the artist was set by the fan and the fan saves Applied
- **THEN** no snack appears
