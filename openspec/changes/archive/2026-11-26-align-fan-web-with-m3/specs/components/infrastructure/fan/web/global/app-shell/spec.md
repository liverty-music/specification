## RENAMED Requirements

- FROM: `### Requirement: Tab switches cross-fade`
- TO: `### Requirement: Screen changes follow their navigation level`

## MODIFIED Requirements

### Requirement: Screen changes follow their navigation level

Every change of the screen shown SHALL animate according to the kind of navigation it is, so the fan sees one screen give way to the next instead of a cut. The navigation bar and the page header SHALL stay in place without fading.

- **Switching between the tabs of the bottom navigation bar** is a top-level change: the outgoing route SHALL fade out quickly and only then the incoming route SHALL fade in, so that the two are not both visible at full strength. Nothing slides, because top-level destinations are not related to each other and the fan cannot swipe between them. The whole change SHALL take 200 ms or less.
- **Opening a screen from inside a page, and going back from it** (for example opening a concert's page from the timetable, opening the link of a notification, or moving from a region to its prefectures inside a sheet) is a forward or backward change: the outgoing screen SHALL fade out and the incoming screen SHALL fade in, completing within 500 ms. Going back SHALL use the same motion as going forward.

Any other change of the screen shown (a redirect, the first load, a deep link) SHALL be shown without animation. Under reduced motion every animated change, and every other animated screen change, SHALL be a short fade of 100 ms or less and SHALL NOT include any movement.

#### Scenario: Tab switch

- **WHEN** the fan taps the My Artists tab while the Timetable is shown
- **THEN** the Timetable fades out first and My Artists fades in after it, within 200 ms in total
- **AND** the two routes are not both at full opacity at the same time
- **AND** the navigation bar and the page header do not fade

#### Scenario: Route change from inside a page

- **WHEN** the fan opens a concert's concert page from the timetable
- **THEN** the timetable fades out and the concert page fades in, within 500 ms
- **AND** the navigation bar and the page header do not fade

#### Scenario: Going back

- **WHEN** the fan goes back from the concert page to the timetable
- **THEN** the concert page fades out and the timetable fades in, within 500 ms, with the same motion as going forward

#### Scenario: Drilling into a sheet's next level

- **WHEN** the fan picks a region in the area sheet and its prefectures replace the regions
- **THEN** the regions fade out and the prefectures fade in, within 500 ms, and going back uses the same motion

#### Scenario: Redirect and first load

- **WHEN** the app opens, at a deep link or through a redirect from the first address
- **THEN** the first route is shown without animation
- **AND** a redirect during a later navigation is part of that screen change and moves as it does

#### Scenario: Reduced motion preference

- **WHEN** the fan has asked the system for reduced motion and taps another tab or opens a concert page
- **THEN** the new route is shown through a fade of 100 ms or less, with no movement

### Requirement: Press is acknowledged by a state layer and shape morph

Tappable controls (buttons and interactive cards) across the app SHALL
acknowledge a press within the short motion band while they are pressed: a
state layer over the control, in the control's content colour at the shared
pressed opacity (Material 3 "States"), that clears on release. A common button
SHALL also morph its corners toward square while pressed (Material 3 button
"Shape morph"). No control SHALL scale when pressed, with one exception: the
handle of a toggle switch grows while pressed (see the Settings route's switch
requirement). Material 3 defines no press scale for any other control. The
acknowledgement SHALL be expressed in stylesheets keyed off
the pressed state, so it costs nothing until a control is pressed and adds no
per-control work when a screen is built. The clickable hit area SHALL stay
stable while the visual shape changes.

#### Scenario: Pressing a control shows the state layer and shape change

- **WHEN** a user presses a button or tappable card
- **THEN** a state layer appears over it and clears on release
- **AND** a common button's corners become smaller (more square) and return on
  release, while a card keeps its shape
- **AND** no control other than a toggle switch's handle changes its size (no scale)

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
