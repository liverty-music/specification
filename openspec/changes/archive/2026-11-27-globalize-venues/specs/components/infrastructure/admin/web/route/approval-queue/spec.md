## MODIFIED Requirements

### Requirement: Admin console approval-queue UI

The admin console SHALL provide a reviewer screen that lists pending concerts grouped
first by performing artist and then by series title, and offers per-concert approve and
reject (with reason) actions. The screen SHALL live in the bundle-isolated `admin/` app
and SHALL consume the admin `ConcertCandidateService`. Grouping SHALL be computed client-side
from the flat `ConcertCandidateService.List` result using the `ConcertCandidate.performer.name` and
`ConcertCandidate.title` fields as grouping keys (artist and series proxy respectively).

Each series group SHALL be presented as a collapsible disclosure. The collapsed summary
SHALL show the series title, the count of pending concerts in the group, and the count
of concerts with an unresolved venue. Individual concert rows within an expanded group
SHALL retain the full set of reviewable fields (local date, start time, open time, listed
venue name, admin area, time zone, resolved place, source URL, discovered timestamp) and their
per-row approve and reject controls. The resolved place SHALL be shown as a link that opens
the place in Google Maps by its resolved place id, or as an unresolved indicator when the
concert has none; no venue name or coordinates from the map catalog are shown. The Artist
and Title columns SHALL NOT be repeated inside the group table; they are conveyed by the
group headers.

#### Scenario: Reviewer sees pending concerts grouped by artist and series

- **WHEN** an authenticated admin opens the approval-queue screen
- **THEN** the pending concerts SHALL be displayed grouped first by performing artist
- **AND** within each artist they SHALL be grouped into collapsible series using the
  concert title as the series proxy
- **AND** each collapsed series summary SHALL show the series title, the number of
  pending concerts in the group, and the number with an unresolved venue

#### Scenario: Expanding a series reveals per-concert review rows

- **WHEN** the admin expands a series group
- **THEN** each pending concert in that series SHALL be listed showing local date,
  start time, open time, listed venue name, admin area, time zone, resolved place as a
  Google Maps link (or unresolved indicator), source URL, and discovered timestamp
- **AND** each row SHALL expose Approve and Reject controls

#### Scenario: Reviewer approves an item

- **WHEN** the admin approves a pending concert
- **THEN** the UI SHALL call `Approve` and remove the row from its series group on success
- **AND** if the series group becomes empty it SHALL be removed from the UI

#### Scenario: Reviewer rejects an item with a reason

- **WHEN** the admin rejects a pending concert and provides a reason
- **THEN** the UI SHALL call `Reject` with that reason and remove the row from its
  series group on success
- **AND** if the series group becomes empty it SHALL be removed from the UI

#### Scenario: Conflict dialog shows open time for both the candidate and the existing event

- **WHEN** approval detects a duplicate and presents the conflict dialog
- **THEN** the dialog SHALL show the open time for both the candidate and the existing event
- **AND** absent open time values SHALL be displayed as a dash placeholder

## ADDED Requirements

### Requirement: The admin gives or corrects the area and time zone of a concert candidate

Each concert row SHALL show its admin area by code, or 地域不明 when it has none, and its time zone, or タイムゾーン不明 when it has none. Every row SHALL offer an area input that takes a code or a name in English or Japanese (`US-CA`, `California`, `東京都`), required when the row has no admin area, and a time zone select, required when the row has no time zone. The select SHALL list the time zones of the country of the area the admin entered, which the screen learns by resolving the entered text through the admin AreaService.Resolve; until the admin enters an area, it SHALL list those of the country of the row's admin area. Each time zone SHALL be shown by the name the API gives for it (its exemplar city, such as ロサンゼルス; Asia/Tokyo is 日本). When the entered text does not resolve, the row SHALL say the area was not found and the select SHALL list no time zone. When the area entered, or else the row's admin area, has a time zone of its own, that time zone SHALL be selected. Approve SHALL stay disabled while a required input is empty or the entered area does not resolve. Approving SHALL send the area input's text and the selected time zone, each when given. When Approve fails with InvalidArgument, the row SHALL stay and say that the area or the time zone was not accepted.

#### Scenario: Area and time zone unknown

- **WHEN** the admin expands a series group with a concert that has no admin area and no time zone
- **THEN** the row shows 地域不明 and タイムゾーン不明, an area input and a time zone select, and its Approve control is disabled

#### Scenario: Area given by name

- **WHEN** the admin enters Texas in that row's area input
- **THEN** the screen resolves it through AreaService.Resolve to US-TX and the time zone select lists the time zones of the US by name, with none selected

#### Scenario: Area and time zone given

- **WHEN** the admin enters Texas in that row's area input, selects シカゴ (America/Chicago) and approves
- **THEN** the UI calls Approve with the area Texas and the time zone America/Chicago and removes the row on success

#### Scenario: Area with a time zone of its own

- **WHEN** the admin enters 東京都 in the area input of a row without a time zone
- **THEN** the time zone select shows 日本 (Asia/Tokyo) selected and Approve is enabled

#### Scenario: Discovered area until one is entered

- **WHEN** a row has the admin area US-TX, no time zone, and an empty area input
- **THEN** the time zone select lists the time zones of the US

#### Scenario: Area present but wrong

- **WHEN** a row shows the admin area JP-13 and the admin enters JP-27 in its area input and approves
- **THEN** the UI calls Approve with the area JP-27

#### Scenario: Area not found

- **WHEN** the admin enters JP-99 in the area input
- **THEN** the row says the area was not found, the time zone select lists no time zone, and Approve is disabled

#### Scenario: Approval refused

- **WHEN** the admin approves and Approve fails with InvalidArgument
- **THEN** the row stays and says that the area or the time zone was not accepted
