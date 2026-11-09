## ADDED Requirements

### Requirement: Month-jump buttons move the timetable between months

The timetable SHALL offer two month-jump buttons, previous month and next month, side by side in one capsule above the FAB. The previous-month button SHALL move the timetable so that the first date of the month before the month at the top of the screen is at the top; the next-month button SHALL do the same for the month after it. A button SHALL be hidden when no loaded date lies in a month in its direction. In a browser that can tell whether a list has been scrolled from its top, both buttons SHALL stay hidden until the fan has scrolled the timetable away from its top; in other browsers the buttons SHALL be shown from the start. In every browser the rule that hides a button with no month in its direction SHALL still apply, and both buttons SHALL be hidden while the FAB's action list is open. Each button SHALL show an icon only, and SHALL be named for assistive technology with the target month (for example "12月へ移動" / "Go to December"). The move SHALL scroll smoothly, and SHALL be instant when the fan has asked the system for reduced motion. A move SHALL NOT add a browser history entry.

#### Scenario: Next month from the middle of November

- **WHEN** the top of the screen shows a November date, December has loaded dates, and the fan taps the next-month button
- **THEN** the timetable shows the first loaded December date at the top of the screen
- **AND** the browser's back action still leaves the dashboard, as before the tap

#### Scenario: Previous month

- **WHEN** the top of the screen shows a December date, November has loaded dates, and the fan taps the previous-month button
- **THEN** the timetable shows the first loaded November date at the top of the screen

#### Scenario: No month in that direction

- **WHEN** the top of the screen shows a date in the last month that has loaded dates
- **THEN** the next-month button is hidden and the previous-month button is shown

#### Scenario: Not shown before the fan scrolls

- **WHEN** the timetable is first displayed and the fan has not scrolled it, in a browser that can tell whether a list has been scrolled from its top
- **THEN** neither month-jump button is shown

#### Scenario: First display in a browser that cannot tell whether a list has been scrolled

- **WHEN** the timetable is first displayed at its first loaded date, in a browser that cannot tell whether a list has been scrolled from its top, and later months have loaded dates
- **THEN** the next-month button is shown and the previous-month button is hidden

#### Scenario: Hidden while the FAB is open

- **WHEN** the fan opens the FAB's action list
- **THEN** both month-jump buttons are hidden until the list closes

#### Scenario: Named for assistive technology

- **WHEN** a screen reader focuses the next-month button while the top of the screen shows a November date
- **THEN** it announces the move to December in the active language

#### Scenario: Reduced motion

- **WHEN** the fan has asked the system for reduced motion and taps a month-jump button
- **THEN** the target month is shown at the top without a scrolling animation

## MODIFIED Requirements

### Requirement: The timetable renders a window of dates around the fan

The timetable SHALL build only the date groups in a window around where the fan
is looking, not every loaded date. On a first visit the window starts at the
first date; on re-entry it starts at the date the fan left the timetable on;
after a month jump it starts at the first date of the target month, and the
dates between the old window and the target are not built. As the fan scrolls
toward either edge of the window, further dates SHALL be added on that side
before the fan reaches the edge, so scrolling never stops at an artificial end.
Adding dates above the fan SHALL NOT move what the fan is looking at. While a
month jump is still scrolling, no dates SHALL be added; adding resumes when the
scroll ends. Dates outside the window SHALL NOT be built. Lane alignment with
the stage header SHALL hold for every group.

#### Scenario: Only the window is built

- **WHEN** a timetable with 225 loaded dates is first displayed or restored on re-entry
- **THEN** at most 24 date groups SHALL be built
- **AND** the number built SHALL NOT depend on how many dates are loaded

#### Scenario: Scrolling down reaches every later date

- **WHEN** the fan scrolls toward the last built date
- **THEN** later dates SHALL be added before the fan reaches the end of the
  built content
- **AND** continuing to scroll SHALL reach the last loaded date

#### Scenario: Scrolling up from a restored date reaches earlier dates without a jump

- **WHEN** the timetable was restored deep in the list and the fan scrolls up
- **THEN** earlier dates SHALL be added above
- **AND** the date the fan is looking at SHALL stay where it is on screen while
  they are added

#### Scenario: A month jump builds only around the target month

- **WHEN** the fan jumps from November to a December that starts 40 loaded dates later
- **THEN** at most 24 date groups SHALL be built after the jump
- **AND** the November dates the fan scrolled past SHALL be built again only when
  the fan scrolls up to them, with the date the fan is looking at staying where
  it is on screen

#### Scenario: Lanes stay aligned in every built group

- **WHEN** any date group is built, including one added while scrolling
- **THEN** its lane columns SHALL align with the stage header's columns
