## Purpose

Establishes that continuous work in the app — animation frame loops, physics
simulation, canvas painting — runs only while the surface it produces is actually
being rendered. Without this each surface decides for itself, and a surface that
forgets keeps a device busy drawing something nobody can see.

## ADDED Requirements

### Requirement: Continuous work suspends when its surface is not rendered

A surface that performs continuous per-frame work SHALL suspend that work
whenever the browser is not rendering it, and SHALL resume it in time for the
content to be correct when seen. This SHALL hold for every reason the browser
stops rendering a surface, including the surface being scrolled out of view and
the page being in a background tab. Suspension SHALL be driven by the browser's
own rendering lifecycle rather than by a separate judgement about visual
visibility, so that work stops for the same reasons and at the same times the
browser stops painting.

Suspension SHALL be invisible to the fan: resuming SHALL NOT show a partially
drawn frame, and SHALL NOT require the fan to interact to restore the surface.

#### Scenario: Work stops when the surface scrolls out of view

- **WHEN** a surface performing continuous per-frame work is scrolled out of view
- **THEN** that work SHALL stop
- **AND** it SHALL resume when the surface is about to be rendered again

#### Scenario: Work stops in a background tab

- **WHEN** the page hosting such a surface moves to a background tab
- **THEN** the work SHALL stop
- **AND** it SHALL resume when the page returns to the foreground

#### Scenario: Resuming is not visible as a glitch

- **WHEN** a suspended surface resumes
- **THEN** it SHALL present a complete frame
- **AND** the fan SHALL NOT have to interact with it to make it render

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
