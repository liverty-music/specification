# Delta for timetable

## MODIFIED Requirements

### Requirement: Empty timetable offers the Concerts view

Whenever the timetable shows an empty timetable to a signed-in fan, the empty state SHALL offer, next to its link to Discovery, a second link that opens the Concerts view on Discovery (`/discovery?view=concerts`). This holds for the fan who follows no artist and for the fan whose followed artists have no concert to show. A guest's empty state SHALL offer only the link to Discovery, since the Concerts view is a signed-in fan's.

#### Scenario: Guest with no follows
- **WHEN** a guest who follows no artist opens the timetable
- **THEN** the empty state shows the link to Discovery and no link 「ライブを探す」

#### Scenario: Signed-in fan with no follows
- **WHEN** a signed-in fan who follows no artist opens the timetable
- **THEN** the empty state shows the link to Discovery and a link 「ライブを探す」
- **AND** tapping 「ライブを探す」 opens Discovery on the Concerts view

#### Scenario: Followed artists with nothing to show
- **WHEN** a signed-in fan follows artists but none of them has a concert to show
- **THEN** the empty state shows the link to Discovery and the link 「ライブを探す」
- **WHEN** a guest follows artists but none of them has a concert to show
- **THEN** the empty state shows the link to Discovery only

#### Scenario: Timetable with concerts
- **WHEN** the timetable shows at least one concert
- **THEN** no link to the Concerts view is shown on the timetable
