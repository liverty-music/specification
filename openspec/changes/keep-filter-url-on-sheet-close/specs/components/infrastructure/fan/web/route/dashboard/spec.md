## ADDED Requirements

### Requirement: Closing the detail sheet keeps the dashboard's filters in the URL

When the concert detail sheet closes by the sheet's own means (light dismiss, swipe down or its close control), the URL SHALL return to the dashboard URL the fan was on when the sheet opened, query parameters included, so the URL always restores the timetable the fan is looking at. A sheet auto-opened from a `/concerts/:id` deep-link SHALL close to the dashboard URL carrying the artist filter the deep-link derived. Closing SHALL still revert the URL via `history.replaceState` without triggering router navigation, and closing by the browser back button SHALL remain the browser's own navigation.

#### Scenario: Closing keeps the active filters in the URL

- **WHEN** the detail sheet is opened while the dashboard is filtered (for example `/dashboard?artists=<id>`, a journey facet or a `from` date)
- **AND** the fan closes the sheet by light dismiss, swipe down or the sheet's own close control
- **THEN** the URL SHALL be that same filtered dashboard URL, query parameters included
- **AND** reloading that URL SHALL show the same filtered timetable the fan was looking at

#### Scenario: Closing a deep-linked sheet returns to the filtered dashboard URL

- **WHEN** the fan closes a detail sheet that was auto-opened from a `/concerts/:id` deep-link
- **THEN** the URL SHALL be `/dashboard?artists=<concert.artistId>`, the filter the deep-link derived
- **AND** reloading that URL SHALL show the same filtered timetable
