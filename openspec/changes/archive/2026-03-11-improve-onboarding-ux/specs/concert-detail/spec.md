## MODIFIED Requirements

### Requirement: Concert Detail View

The system SHALL provide a detail view for a selected concert using a popover-based sheet (not a modal dialog), ensuring compatibility with coach mark overlays in the top layer.

#### Scenario: Open detail from dashboard

- **WHEN** a user taps a concert card on the dashboard
- **THEN** the system SHALL open a bottom sheet displaying the concert detail
- **AND** the sheet SHALL use `popover="manual"` with `showPopover()` (not `<dialog>.showModal()`)
- **AND** the sheet element SHALL be a `<dialog popover="manual">` providing native dialog semantics (implicit `role="dialog"`)
- **AND** the URL SHALL update to `/concerts/:id` via `history.pushState` without triggering full page navigation

#### Scenario: Display venue information

- **WHEN** the concert detail view is open
- **THEN** it SHALL display the venue name (`listed_venue_name`) and administrative area (`venue.admin_area`) if available

#### Scenario: Google Maps link

- **WHEN** the concert detail view is open
- **THEN** it SHALL render a tappable link that opens Google Maps with a query composed of venue name and admin area

#### Scenario: Ticket / official info link

- **WHEN** the concert detail view is open and `source_url` is present
- **THEN** it SHALL render a "View Official Info" button linking to `source_url` in a new tab

#### Scenario: Dismiss sheet (non-onboarding)

- **WHEN** the user swipes down or taps outside the sheet
- **AND** the user is NOT in onboarding Step 4
- **THEN** the sheet SHALL call `hidePopover()` and the URL SHALL revert to the dashboard URL

#### Scenario: Sheet non-dismissible during onboarding Step 4

- **WHEN** the user is at onboarding Step 4
- **THEN** the sheet SHALL NOT be dismissible (no swipe-down, no outside tap, no escape key)
- **AND** the coach mark overlay SHALL appear above the sheet in the top layer, targeting `[data-nav-my-artists]`
