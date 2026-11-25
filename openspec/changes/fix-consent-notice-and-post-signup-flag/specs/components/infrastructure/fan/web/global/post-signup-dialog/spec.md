## ADDED Requirements

### Requirement: The post-signup sequence survives closing the app

The one-shot marker that schedules the celebration and the post-signup dialog after a sign-up SHALL be spent when the dialog opens, not when the celebration appears or when the Timetable waits for the concert sheet. A fan who closes the app, or leaves the Timetable, before the dialog has opened SHALL get the sequence on their next visit to the Timetable.

#### Scenario: App closed during the celebration

- **WHEN** a newly signed-up fan sees the celebration overlay and closes the app before dismissing it
- **AND** later opens the Timetable again
- **THEN** the celebration overlay is shown again
- **AND** the post-signup dialog opens once it is dismissed, and the marker is spent only then

#### Scenario: App closed before the concert sheet closes

- **WHEN** a fan who signed up from a concert sheet's ticket sale notification button closes the app while that sheet is still open
- **AND** later opens the Timetable again
- **THEN** the post-signup dialog opens as soon as the Timetable shows no concert detail sheet, with its notification step, and the marker is spent only then
