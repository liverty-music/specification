## MODIFIED Requirements

### Requirement: Spotlight Visual Layer via Box-Shadow

The coach mark SHALL dim the whole viewport to 70% black except for a cutout over its target, and SHALL outline the cutout with the brand accent border. The cutout SHALL extend 8px beyond the target on every side and SHALL use the corner radius the screen gives for its target (12px when none is given). The dim layer SHALL never take taps: a tap on the dimmed area reaches the page beneath it.

#### Scenario: Spotlight renders with rounded cutout over target

- **WHEN** a coach mark is shown for a target
- **THEN** the viewport outside the cutout is dimmed to 70% black
- **AND** the cutout shows the target undimmed with rounded corners
- **AND** a tap on the dimmed area reaches the page element beneath it

#### Scenario: Spotlight shape adapts per step

- **WHEN** the screen gives a corner radius of 50% for a circular target
- **THEN** the cutout is a circle
- **WHEN** the screen gives no corner radius
- **THEN** the cutout corners are 12px

#### Scenario: Spotlight cutout has padding around target

- **WHEN** the spotlight is positioned over a target element
- **THEN** the cutout extends 8px beyond the target's bounds on all sides

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark surface that highlights one target element as a non-blocking hint with a short message. The screen that uses a coach mark SHALL name its target within its own content (for example, the first concert card of the Welcome demo timetable), so that the coach mark never highlights an element of another surface. The message SHALL carry the accessible label "Onboarding tip". A tap on the highlighted target SHALL perform the target's own action, exactly as a tap on the target would without the coach mark, and SHALL then close the coach mark. The coach mark SHALL render as a fixed layer over the whole viewport that never takes taps itself, except over the highlighted target.

#### Scenario: Spotlight renders for active coach mark

- **WHEN** a screen shows a coach mark
- **THEN** the spotlight and the message appear over the target
- **AND** the message's accessible label is "Onboarding tip"

#### Scenario: Nav tab tap through spotlight delegates to href

- **WHEN** a coach mark highlights a link
- **AND** the user taps the highlighted link
- **THEN** the link navigates as a direct tap on it would
- **AND** the coach mark closes

#### Scenario: Target tap performs the target's own action

- **WHEN** the Welcome demo coach mark highlights a concert card
- **AND** the visitor taps the highlighted card
- **THEN** the concert detail sheet for that card opens, as a direct tap on the card opens it
- **AND** the coach mark closes

#### Scenario: Off-target tap light-dismisses without blocking the page

- **WHEN** a coach mark is shown
- **AND** the user taps the dimmed area outside the highlighted target
- **THEN** the coach mark closes
- **AND** the tap still reaches the underlying page
- **AND** page scroll remains enabled

#### Scenario: Target selector is scoped to component context

- **WHEN** the Welcome demo shows its coach mark
- **THEN** the coach mark highlights a concert card of the demo timetable
- **AND** it never highlights an element of another surface, such as a help sheet

### Requirement: Route Detach Spotlight Cleanup

When the user leaves a screen that shows a coach mark, the coach mark SHALL close and leave nothing on screen.

#### Scenario: Route detaching cleans up spotlight

- **WHEN** a coach mark is shown on a screen
- **AND** the user navigates to another screen
- **THEN** the coach mark closes before the next screen shows
- **AND** no spotlight, message or dimmed layer remains

#### Scenario: Navigation during active spotlight does not throw

- **WHEN** a coach mark is shown
- **AND** the user navigates away by any means (a link, browser back, or a tap on the highlighted target)
- **THEN** the navigation completes without an error

### Requirement: Tooltip Anchor Positioning

The coach mark message SHALL be placed directly below its target, and above the target when there is not enough room below it in the viewport.

#### Scenario: Tooltip appears below target

- **WHEN** a coach mark is shown and there is room below the target
- **THEN** the message appears directly below the target

#### Scenario: Message flips above the target

- **WHEN** a coach mark is shown and the message does not fit below the target
- **THEN** the message appears directly above the target

### Requirement: Tooltip Visual Treatment

The coach mark message SHALL render as white text with no background or shadow, directly on the dimmed layer, in the app's base UI font, at most 320px wide, and SHALL break Japanese text at phrase boundaries with balanced line lengths.

#### Scenario: Tooltip renders without solid background

- **WHEN** the coach mark message is displayed
- **THEN** the text is white on the 70% black dimmed layer with no background box or shadow
- **AND** the text uses the app's base UI font

#### Scenario: Japanese message breaks at phrase boundaries

- **WHEN** the message 「カードをタップして、チケットや会場をチェック」 wraps onto two lines
- **THEN** no word such as 「チケット」 is split across the lines

### Requirement: Invisible Target Rejection

The coach mark SHALL treat a target with zero width and zero height as not yet present, keep looking for a visible target for up to 5 seconds after the screen asks for it, and SHALL show nothing if no visible target appears within those 5 seconds.

#### Scenario: Zero-dimension target is skipped

- **WHEN** the target element exists but has zero width and zero height
- **THEN** the coach mark is not shown yet
- **AND** it is shown as soon as the target becomes visible within 5 seconds

#### Scenario: Hidden element in closed popover is skipped

- **WHEN** the target matches an element inside a closed sheet or a hidden container, so it has zero size
- **THEN** the coach mark is not shown for that element
- **AND** it keeps looking for a visible target until 5 seconds have passed

#### Scenario: Target never becomes visible

- **WHEN** no visible target appears within 5 seconds
- **THEN** the coach mark is not shown

## ADDED Requirements

### Requirement: One non-blocking coach mark rendered by the screen that uses it

The coach mark SHALL be a single, transient, non-blocking hint. At most one coach mark SHALL be shown at a time. It SHALL NOT lock page scroll and SHALL NOT block interaction with the rest of the page. The screen that uses a coach mark SHALL render it within that screen; today the only such screen is Welcome, for its demo timetable. The coach mark SHALL close when the user taps its target, taps outside it, or leaves the screen.

#### Scenario: Coach mark does not block the rest of the page

- **WHEN** a coach mark is shown
- **THEN** the page outside the highlighted target remains interactive
- **AND** page scroll is not locked

#### Scenario: Only the Welcome demo shows a coach mark

- **WHEN** a fan uses Discovery, the Dashboard or My Artists
- **THEN** no coach mark is shown on those screens
- **WHEN** a visitor reaches the interactive timetable of the Welcome demo
- **THEN** the Welcome screen may show its coach mark, and at most one coach mark is shown

#### Scenario: Coach mark closes on any tap or on leaving the screen

- **WHEN** the user taps the coach mark target, OR taps outside it, OR leaves the screen
- **THEN** the coach mark closes and its spotlight, message and dimmed layer are removed

### Requirement: Welcome demo coach mark timing

The coach mark SHALL be owned independently of onboarding state and SHALL never change it. On Welcome, the coach mark SHALL appear 5 seconds after the demo timetable becomes interactive, highlighting the first concert card with the message 「カードをタップして、チケットや会場をチェック」, unless the visitor has already tapped a card. It SHALL not be remembered: it can appear again on a later visit to Welcome.

| Action       | From       | To         |
|--------------|------------|------------|
| Activation   | `inactive` | `active`   |
| Deactivation | `active`   | `inactive` |

#### Scenario: Coach mark appears after 5 seconds

- **WHEN** the Welcome demo timetable has been interactive for 5 seconds
- **AND** the visitor has not tapped a concert card
- **THEN** the coach mark moves from `inactive` to `active` on the first concert card

#### Scenario: A card tap before 5 seconds cancels the coach mark

- **WHEN** the visitor taps a concert card before the 5 seconds pass
- **THEN** the coach mark does not appear on that visit to the demo

#### Scenario: Welcome coach mark deactivates on tap or leaving

- **WHEN** the highlighted card is tapped, OR the visitor taps outside it, OR leaves Welcome
- **THEN** the coach mark moves from `active` to `inactive`
- **AND** onboarding state is unchanged

## REMOVED Requirements

### Requirement: Single Transient Non-Blocking Coach Mark

**Reason**: It placed one coach mark in the app shell, driven for Discovery. Discovery no longer shows a coach mark; the Welcome demo renders its own.
**Migration**: See "One non-blocking coach mark rendered by the screen that uses it".

### Requirement: Coach mark is an independent, non-blocking hint

**Reason**: It activated the coach mark on Discovery when follow counts crossed 5 follows or 3 artists with concerts. Discovery shows a progress row instead (see the Discovery screen).
**Migration**: See "Welcome demo coach mark timing" for the remaining coach mark.

### Requirement: Spotlight Uses Popover Top Layer

**Reason**: The coach mark renders as a fixed, full-viewport layer that never takes taps, not as a top-layer popover; nothing in the product uses the popover model.
**Migration**: The fixed-layer behaviour is stated in "Coach Mark Overlay System" and "Spotlight Visual Layer via Box-Shadow".

### Requirement: Coach Mark Target Click Delegates Navigation to Aurelia Router

**Reason**: No coach mark highlights a navigation link any more; the only coach mark (Welcome demo) highlights a concert card.
**Migration**: A tap on the target performs the target's own action, as stated in "Coach Mark Overlay System".

### Requirement: Smooth Spotlight Movement via View Transitions API

**Reason**: The coach mark never moves between targets or across screens; it shows one target and closes. No view transition runs.
**Migration**: None. A future multi-target coach mark would specify its own movement.

### Requirement: Inline SVG Directional Arrow

**Reason**: The coach mark message has no arrow; the spotlight outline and the message placement show the target.
**Migration**: None.

### Requirement: Coach Mark Navigation Delegation

**Reason**: Discovery no longer shows a coach mark on the Home tab; it shows a progress row instead (see the Discovery screen). No coach mark highlights a navigation tab.
**Migration**: A tap on the target performs the target's own action, as stated in "Coach Mark Overlay System".
