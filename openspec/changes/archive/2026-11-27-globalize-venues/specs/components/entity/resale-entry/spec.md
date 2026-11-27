## MODIFIED Requirements

### Requirement: Draw times of an event

An event's resale draws SHALL run at 12:00 in the time zone of the event's Venue on every day before the event's day, and once on the event's day at the event's resale deadline, which is the last draw of the event. The days are the calendar days at the Venue (entity/venue "Current date at a venue").

#### Scenario: Day before the event
- **WHEN** an event starts at 19:00 on 10 November
- **THEN** a draw runs at 12:00 on 9 November and it is not the last draw

#### Scenario: Evening show
- **WHEN** an event starts at 19:00 on 10 November, so its resale deadline is 12:00
- **THEN** the last draw runs at 12:00 on 10 November

#### Scenario: Matinee
- **WHEN** an event starts at 14:00 on 10 November, so its resale deadline is 11:00
- **THEN** the last draw runs at 11:00 on 10 November and no draw runs at 12:00 that day

#### Scenario: Event abroad
- **WHEN** an event at a Venue in Europe/London starts at 19:30 on 10 November 2026
- **THEN** a draw runs at 12:00 London time on 9 November, which is 21:00 in Japan time, and the last draw runs at 12:00 London time on 10 November
