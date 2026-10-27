## ADDED Requirements

### Requirement: Empty timetable offers the All Nearby view

Whenever the dashboard shows an empty timetable, the empty state SHALL offer, next to its link to Discovery, a second link that opens the All Nearby view on Discovery (`/discovery?view=nearby`). This holds for the guest who follows no artist and for the fan whose followed artists have no concert to show.

#### Scenario: Guest with no follows
- **WHEN** a guest who follows no artist opens the dashboard
- **THEN** the empty state shows the link to Discovery and a link 「近くのライブを見る」
- **AND** tapping 「近くのライブを見る」 opens Discovery on the All Nearby view

#### Scenario: Followed artists with nothing to show
- **WHEN** a fan follows artists but none of them has a concert to show
- **THEN** the empty state shows the link to Discovery and the link 「近くのライブを見る」

#### Scenario: Timetable with concerts
- **WHEN** the timetable shows at least one concert
- **THEN** no link to the All Nearby view is shown on the dashboard

## MODIFIED Requirements

### Requirement: The timetable renders a window of dates around the fan

The timetable SHALL build only the date groups in a window around where the fan
is looking, not every loaded date. On a first visit the window starts at the
first date; on re-entry it starts at the date the fan left the timetable on.
As the fan scrolls toward either edge of the window, further dates SHALL be
added on that side before the fan reaches the edge, so scrolling never stops at
an artificial end. Adding dates above the fan SHALL NOT move what the fan is
looking at. Dates outside the window SHALL NOT be built. Lane alignment with the
stage header SHALL hold for every group.

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

#### Scenario: Lanes stay aligned in every built group

- **WHEN** any date group is built, including one added while scrolling
- **THEN** its lane columns SHALL align with the stage header's columns

### Requirement: Dashboard routes event selection and shows its loading states

`dashboard-route` SHALL handle event selection and loading/empty states directly. Selecting a first-party concert SHALL navigate to its Event page (`/events/:id`); selecting a discovered concert SHALL open the `event-detail-sheet` dialog. Returning from the Event page SHALL show the timetable at the date the fan left it on.

#### Scenario: Event selection handled by dashboard
- **WHEN** a user taps a discovered concert's card in the concert list
- **THEN** `dashboard-route` SHALL handle the `event-selected` custom event and open the `event-detail-sheet` dialog

#### Scenario: First-party concert opens its event page
- **WHEN** a user taps the card of a concert whose Series belongs to an Organizer, in the timetable
- **THEN** the app SHALL navigate to `/events/<id>` and SHALL NOT open the detail sheet

#### Scenario: Back from the event page
- **WHEN** the fan opened an Event page from a card dated 2026-11-20 deep in the timetable and goes back
- **THEN** the dashboard shows the timetable at 2026-11-20

#### Scenario: Loading and empty states
- **WHEN** the fan's concerts are still loading
- **THEN** the timetable SHALL show its loading placeholder in place of the lanes, and no empty state
- **WHEN** they have loaded and none match
- **THEN** the dashboard SHALL show the empty state with a link to Discovery

## REMOVED Requirements

### Requirement: All Nearby mode uses ListByLocation
**Reason**: The All Nearby view moved from the dashboard to Discovery; the dashboard shows only the timetable of followed artists.
**Migration**: The same requirement is stated for the All Nearby view on Discovery (discovery spec, ADDED in this change).

### Requirement: Dashboard Mode Toggle
**Reason**: The dashboard has one view, the timetable of followed artists. The All Nearby view moved to Discovery.
**Migration**: Discovery switches between the artist bubbles and the All Nearby view with its swap tile (discovery "Swap tile switches between the artist bubbles and the All Nearby view").

### Requirement: Date Preset Selector
**Reason**: The All Nearby view moved from the dashboard to Discovery; the dashboard shows only the timetable of followed artists.
**Migration**: The same requirement is stated for the All Nearby view on Discovery (discovery spec, ADDED in this change).

### Requirement: Area Selector in All Nearby Mode
**Reason**: The All Nearby view moved from the dashboard to Discovery; the dashboard shows only the timetable of followed artists.
**Migration**: The same requirement is stated for the All Nearby view on Discovery (discovery spec, ADDED in this change).

### Requirement: All Nearby Concert List
**Reason**: The All Nearby view moved from the dashboard to Discovery; the dashboard shows only the timetable of followed artists.
**Migration**: The same requirement is stated for the All Nearby view on Discovery (discovery spec, ADDED in this change).

### Requirement: Follow CTA in Event Detail Sheet for All Nearby
**Reason**: The follow action in the event detail sheet is stated once, by the bottom-sheet surface.
**Migration**: bottom-sheet "Follow CTA in Event Detail Sheet", which now names the All Nearby view on Discovery.

### Requirement: Compact All Nearby Filter Bar
**Reason**: The All Nearby view moved from the dashboard to Discovery; the dashboard shows only the timetable of followed artists.
**Migration**: The same requirement is stated for the All Nearby view on Discovery (discovery spec, ADDED in this change).

### Requirement: Localized All Nearby Date Display
**Reason**: The All Nearby view moved from the dashboard to Discovery; the dashboard shows only the timetable of followed artists.
**Migration**: The same requirement is stated for the All Nearby view on Discovery (discovery spec, ADDED in this change).

### Requirement: Natural Japanese Copy for All Nearby
**Reason**: The All Nearby view moved from the dashboard to Discovery; the dashboard shows only the timetable of followed artists.
**Migration**: The same requirement is stated for the All Nearby view on Discovery (discovery spec, ADDED in this change).
