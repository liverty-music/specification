## ADDED Requirements

### Requirement: The permission answer is reported

After the fan answers the browser's push-permission request started from the notification prompt or from Settings, the fan app SHALL send one usage analytics event with the answer (granted, denied, or dismissed without an answer) and where the request started.

#### Scenario: Fan denies
- **WHEN** the fan taps Allow on the notification prompt and then blocks notifications in the browser's request
- **THEN** one event is sent with the answer denied and the notification prompt as its start
