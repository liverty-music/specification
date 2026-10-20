## MODIFIED Requirements

### Requirement: Admission window

The admission window of a Scanner SHALL be derived from its event's current local date and start time, in Japan time. It SHALL open 3 hours before the start time and close at 04:00 on the day after the local date; the open time does not affect it, because an event may have none. A time is inside the window when it is at or after the opening and before the closing. An event without a start time SHALL have no admission window.

#### Scenario: Usual evening show

- **WHEN** the event is on 2026-11-20 with open time 18:00 and start time 19:00
- **THEN** the window is from 2026-11-20 16:00 to 2026-11-21 04:00

#### Scenario: No open time

- **WHEN** the event is on 2026-11-20 with start time 19:00 and no open time
- **THEN** the window opens at 2026-11-20 16:00

#### Scenario: Before the window

- **WHEN** the window opens at 16:00 and the time is 15:59
- **THEN** the time is outside the window

#### Scenario: Window closed

- **WHEN** the window closes at 2026-11-21 04:00 and the time is 2026-11-21 04:00
- **THEN** the time is outside the window

#### Scenario: No start time

- **WHEN** the event has no start time
- **THEN** it has no admission window
