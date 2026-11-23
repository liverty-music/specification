## ADDED Requirements

### Requirement: The toggle switch is 52 × 32 px and its handle grows while pressed

Each Settings toggle switch SHALL have a track 52 px wide and 32 px high. Its handle SHALL be 16 px across when the switch is off, 24 px across when the switch is on and 28 px across while the switch is pressed, and SHALL move between the two ends over the app's short motion duration. The grown handle SHALL stay inside the track. The switch's activation target stays at least 24 px on both axes, as "Switch remains operable and accessibly separate" states, and the 52 × 32 px track already meets it. Under reduced motion the handle SHALL change size and position without movement between the states.

#### Scenario: Switch is turned on

- **WHEN** the fan turns a switch on
- **THEN** the handle moves to the on end and is 24 px across
- **AND** the handle stays inside the 52 × 32 px track

#### Scenario: Switch is pressed

- **WHEN** the fan presses a switch
- **THEN** the handle is 28 px across until the press ends
- **AND** the handle stays inside the track and the switch's size does not change

#### Scenario: Reduced motion

- **WHEN** the fan has asked the system for reduced motion and turns a switch on
- **THEN** the handle is shown at the on end without moving there
