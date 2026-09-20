## ADDED Requirements

### Requirement: The beam effect is presentational and costs nothing to render

The laser beam spotlight SHALL be driven by the scroll position of the concert it
is anchored to, without per-frame scripting and without reading the geometry of
any concert card. Reading card geometry to position the beams forces layout of
content the browser would otherwise skip, so it both costs main-thread time
proportional to the number of concerts and defeats viewport-scoped rendering of
the timetable.

The effect SHALL degrade to no beams where the platform cannot drive it, and its
absence SHALL change nothing else: the timetable, the toggle and the persisted
preference SHALL behave identically.

#### Scenario: Beams track scroll position without scripting

- **WHEN** the fan scrolls the timetable with the beam effect enabled
- **THEN** each beam SHALL follow its anchor concert's position
- **AND** no per-frame script SHALL read the position or size of any concert card

#### Scenario: Beams do not defeat viewport-scoped rendering

- **WHEN** the beam effect is enabled on a timetable whose off-screen date groups
  are being skipped
- **THEN** those groups SHALL remain skipped
- **AND** the beams SHALL NOT cause them to be laid out

#### Scenario: Only concerts on screen are lit

- **WHEN** the beam effect is enabled on a timetable longer than the viewport
- **THEN** only the concerts currently on screen SHALL have a beam drawn
- **AND** a concert the fan has not scrolled to SHALL NOT be lit, whether its date
  group is merely below the fold or is being skipped entirely

#### Scenario: Beams are absent where unsupported, with nothing else affected

- **WHEN** the fan's browser cannot drive the effect
- **THEN** no beams SHALL be shown
- **AND** the toggle SHALL still be offered, still persist the preference, and the
  timetable SHALL render and behave exactly as it does with the effect disabled
