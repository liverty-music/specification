## MODIFIED Requirements

### Requirement: The beam effect is presentational and costs nothing to render

The laser beam spotlight SHALL be driven by the scroll position of the concert it
is anchored to, without per-frame scripting and without reading the geometry of
any concert card. Reading card geometry to position the beams forces layout, so
it costs main-thread time proportional to the number of concerts.

The effect is off unless the fan turns it on. While it is off it SHALL add no
work to building or rendering the timetable: no concert card SHALL carry
anything that exists only for the beams. While it is on, its cost SHALL be
proportional to the number of beams drawn, not to the number of cards.

The effect SHALL degrade to no beams where the platform cannot drive it, and its
absence SHALL change nothing else: the timetable, the toggle and the persisted
preference SHALL behave identically.

#### Scenario: Beams track scroll position without scripting

- **WHEN** the fan scrolls the timetable with the beam effect enabled
- **THEN** each beam SHALL follow its anchor concert's position
- **AND** no per-frame script SHALL read the position or size of any concert card

#### Scenario: Beams do not defeat viewport-scoped rendering

- **WHEN** the beam effect is enabled on a timetable whose later dates are not
  yet built
- **THEN** the beams SHALL NOT cause any of those dates to be built
- **AND** a matched concert whose date is not built SHALL have no beam

#### Scenario: Only concerts on screen are lit

- **WHEN** the beam effect is enabled on a timetable longer than the viewport
- **THEN** only the concerts currently on screen SHALL have a beam drawn
- **AND** a concert the fan has not scrolled to SHALL NOT be lit, whether its
  date is merely below the fold or not built at all

#### Scenario: Beams are absent where unsupported, with nothing else affected

- **WHEN** the fan's browser cannot drive the effect
- **THEN** no beams SHALL be shown
- **AND** the toggle SHALL still be offered, still persist the preference, and the
  timetable SHALL render and behave exactly as it does with the effect disabled

#### Scenario: Disabled beams cost nothing

- **WHEN** the beam effect is off and the timetable is built
- **THEN** no concert card SHALL carry a beam timeline, beam index or any other
  beam-only attribute or binding
- **AND** no beam set SHALL be computed

## REMOVED Requirements

### Requirement: Beam tracking updates efficiently per frame
**Reason**: Describes a per-frame scripted tracker (anchor map, geometry reads, style writes) that no longer exists; the beams are driven by CSS scroll timelines, as "The beam effect is presentational and costs nothing to render" requires.
**Migration**: None; the behavior it constrained was deleted in `defer-dashboard-reentry-render`.
