## Purpose

Ensures continuous per-frame work such as animation or simulation runs only while the surface producing it is actually visible, suspending cleanly whenever it leaves view for any reason and resuming without a jump or a visible glitch when it returns.

## ADDED Requirements

### Requirement: Continuous work suspends when its surface is not rendered

A surface that performs continuous per-frame work SHALL suspend that work
whenever the browser is not rendering it, and SHALL resume it before the content
is seen again.

This SHALL hold for every reason the surface stops being rendered. The reasons
are a property of the surface's layout and the page's state, not a fixed list —
a surface hidden by its own route, one scrolled out of a scrolling container, and
one in a background tab are all the same condition for this purpose, and a
surface SHALL be suspended under whichever of them can occur to it.

#### Scenario: Work stops while the surface is not rendered

- **WHEN** a surface performing continuous per-frame work stops being rendered,
  for any reason
- **THEN** that work SHALL stop
- **AND** it SHALL resume before the surface is seen again

#### Scenario: Work stops in a background tab

- **WHEN** the page hosting such a surface moves to a background tab
- **THEN** the work SHALL stop
- **AND** it SHALL resume when the page returns to the foreground

#### Scenario: Resuming is not visible as a glitch

- **WHEN** a suspended surface resumes
- **THEN** it SHALL present a complete frame
- **AND** the fan SHALL NOT have to interact with it to make it render

### Requirement: Overlapping suspension conditions do not cancel each other

Where more than one condition can suspend the same surface, a surface SHALL
remain suspended while any of them still holds. Lifting one condition SHALL NOT
resume work that another condition independently requires to stay stopped.

This is the failure that hides: each condition read on its own looks correct, and
the surface only wakes wrongly when two overlap.

#### Scenario: A second condition keeps the surface suspended

- **WHEN** a surface is suspended for two reasons at once
- **AND** one of those reasons stops applying
- **THEN** the surface SHALL remain suspended while the other still applies
- **AND** it SHALL resume only once none of them applies

### Requirement: Resuming continues the work rather than advancing it

A surface SHALL resume from where it was suspended rather than accounting for the
time that passed while it was stopped. Continuous work computes from the interval
since its previous frame; after a suspension that interval is arbitrarily large,
and applying it would make a simulation jump rather than continue.

#### Scenario: A long suspension does not make the surface lurch

- **WHEN** a surface resumes after being suspended for an extended period
- **THEN** it SHALL continue from the state it was suspended in
- **AND** it SHALL NOT jump, skip ahead, or destabilise as though the elapsed
  time had been simulated

### Requirement: Suspension respects a reduced-motion preference

Suspension and resumption SHALL NOT reintroduce motion that a fan's reduced-motion
preference has suppressed. A surface that paints a single static frame instead of
animating SHALL still be painting that frame after any suspension condition comes
and goes, and SHALL NOT be started into a loop by a resume.

#### Scenario: A resume does not start motion the fan has opted out of

- **WHEN** a fan prefers reduced motion
- **AND** a suspension condition applies to a surface and then stops applying
- **THEN** no continuous work SHALL be started
- **AND** the surface SHALL still show its static content

### Requirement: Suspension never changes what is on screen

Suspending work SHALL NOT alter the surface's appearance while it is suspended:
whatever was last drawn SHALL remain, so a surface that is partially visible, or
becomes visible before work resumes, never shows blank or torn content.

#### Scenario: A suspended surface keeps its last frame

- **WHEN** a surface's continuous work is suspended
- **THEN** the content it had already drawn SHALL remain displayed
- **AND** the surface SHALL NOT clear, blank, or tear

### Requirement: Teardown releases continuous work

A surface SHALL stop its continuous work when it is removed, and SHALL NOT leave
a loop, timer or subscription running behind it.

#### Scenario: Leaving the surface stops its work

- **WHEN** a surface performing continuous work is removed from the page
- **THEN** all of its per-frame work SHALL stop
- **AND** nothing SHALL remain scheduled that would resume it
