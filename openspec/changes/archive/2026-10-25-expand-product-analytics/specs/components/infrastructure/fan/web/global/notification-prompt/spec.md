## ADDED Requirements

### Requirement: The permission answer is reported

After the fan answers the browser's push-permission request, the fan app SHALL send one usage analytics event with the answer (granted, denied, or dismissed without an answer) and where the request started: the push offer after a hype change (the notification prompt), the post-signup sheet, Settings, or checkout.

#### Scenario: Fan denies
- **WHEN** the fan presses 「オンにする」 on the push offer and then blocks notifications in the browser's request
- **THEN** one event is sent with the answer denied and the notification prompt as its start
