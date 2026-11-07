## MODIFIED Requirements

### Requirement: Press is acknowledged by a state layer and shape morph

Tappable controls (buttons and interactive cards) across the app SHALL
acknowledge a press within the short motion band while they are pressed: a
state layer over the control and a shape change (corner morph or slight scale)
that settles on release. The acknowledgement SHALL be expressed in stylesheets
keyed off the pressed state, so it costs nothing until a control is pressed and
adds no per-control work when a screen is built. The clickable hit area SHALL
stay stable while the visual shape changes.

#### Scenario: Pressing a control shows the state layer and shape change

- **WHEN** a user presses a button or tappable card
- **THEN** a state layer appears over it and its shape changes, then both
  settle on release

#### Scenario: Hit target is preserved during the shape change

- **WHEN** the shape change animates
- **THEN** the interactive/clickable bounds remain unchanged and the target
  stays at least 48px

#### Scenario: Reduced motion still acknowledges

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the shape change is not animated but the state layer still confirms
  the press

#### Scenario: Building a screen does no press-related work

- **WHEN** a screen with many tappable cards is built
- **THEN** no work SHALL be performed per control for press acknowledgement
  until a control is pressed
