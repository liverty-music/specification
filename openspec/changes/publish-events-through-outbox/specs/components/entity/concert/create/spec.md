## ADDED Requirements

### Requirement: New concerts are announced per artist and series

For each Series and each Artist newly listed by this call at one or more Events of that Series, Create SHALL announce the new concerts once, carrying those Concerts: the new Events, and the existing Events to which the Artist was newly added. Each announcement SHALL be made together with the change: all are stored or none is. An Artist that already performed at every returned Event of the Series SHALL NOT be announced for it, and a call that returns no Event id SHALL announce nothing. When an announcement cannot be recorded, Create SHALL fail with Unavailable and store nothing.

#### Scenario: Three new events of one tour

- **WHEN** Create stores three new Events of one Series, each performed by Artist A
- **THEN** one announcement for Artist A is made, carrying the three Concerts

#### Scenario: Co-headliner found later

- **WHEN** Artist B is created at an existing Event where only Artist A performs
- **THEN** one announcement for Artist B is made, carrying that Concert, and nothing is announced for Artist A

#### Scenario: Repeated create

- **WHEN** the same Concert with the same performer is created twice
- **THEN** the second Create announces nothing

#### Scenario: Announcement cannot be recorded

- **WHEN** Create would store a new Event and the announcement cannot be recorded
- **THEN** Create fails with Unavailable and stores nothing
