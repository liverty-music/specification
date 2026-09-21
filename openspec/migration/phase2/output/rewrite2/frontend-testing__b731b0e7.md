<!-- spec: frontend-testing | target: components/infrastructure/fan/web/global/event-detail-sheet | flags: CLASSNAME | new_name: Event detail sheet computes URLs and handles touch dismiss -->

### Requirement: Event detail sheet computes URLs and handles touch dismiss
The event detail sheet SHALL compute Google Maps and Calendar URLs and support touch drag-to-dismiss with a 100px threshold.

#### Scenario: Google Maps URL construction
- **WHEN** the sheet is opened with an event that has a venue name
- **THEN** `googleMapsUrl` SHALL return a valid Google Maps search URL for the venue

#### Scenario: Google Calendar URL construction
- **WHEN** the sheet is opened with an event
- **THEN** `calendarUrl` SHALL return a Google Calendar URL with correct start and end times

#### Scenario: Touch drag exceeding threshold closes sheet
- **WHEN** a touch drag moves more than 100px downward
- **THEN** the sheet SHALL close

#### Scenario: Touch drag below threshold keeps sheet open
- **WHEN** a touch drag moves less than 100px
- **THEN** the sheet SHALL remain open
