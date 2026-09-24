# Create Draft

## Purpose

CreateDraft lets an organizer operator start a new first-party concert — a Series with one or more DraftEvents and the Artists it represents as performers — as a DRAFT that no fan can see and nobody is notified about until it is published.

## Requirements

### Requirement: Draft input is validated

CreateDraft SHALL fail with InvalidArgument, storing nothing, when the title is empty, when there is no event, when an event has no date, when an event's date is before the current UTC calendar day, or when an event's open time is after its start time. An empty performer list is accepted in a draft; publishing requires at least one performer.

#### Scenario: No event
- **WHEN** a draft is created with no event
- **THEN** CreateDraft fails with InvalidArgument

#### Scenario: Date in the past
- **WHEN** an event's date is yesterday in UTC
- **THEN** CreateDraft fails with InvalidArgument

#### Scenario: Doors after start
- **WHEN** an event opens at 19:00 and starts at 18:00
- **THEN** CreateDraft fails with InvalidArgument

### Requirement: Only represented artists

CreateDraft SHALL fail with PermissionDenied, without saying which Artist, when any performer is not among the Artists the caller's Organizer represents (Organizer.ListArtists).

#### Scenario: Unrepresented artist
- **WHEN** the draft names an Artist the Organizer does not represent
- **THEN** CreateDraft fails with PermissionDenied and stores nothing

### Requirement: Each event's venue is found or created

For each event, CreateDraft SHALL use the Venue holding the given place id when one is given and held (Venue.GetByPlaceID), else the Venue holding the entered venue name and admin area (Venue.GetByListedName), else create a Venue named after the entered name with the given place id and admin area and no coordinates (Venue.Create). No external place search SHALL be made.

#### Scenario: Known place id
- **WHEN** an event gives a place id that a Venue holds
- **THEN** that Venue is used

#### Scenario: New venue name
- **WHEN** no Venue holds the place id or the entered name and admin area
- **THEN** a Venue named after the entered name is created without coordinates

### Requirement: Draft stored as DRAFT

CreateDraft SHALL store the Series as DRAFT, owned by the caller's Organizer, with one DraftEvent per event — a multi-showtime day being several DraftEvents — and the performers (Series.CreateDraft), and SHALL return the Series with its DraftEvents and performers (Series.GetAuthored). Nothing SHALL be announced.

#### Scenario: Draft for a represented artist
- **WHEN** an operator creates a draft with one event naming a represented Artist
- **THEN** a DRAFT Series owned by the Organizer is returned and no fan list or notification shows it

#### Scenario: Two showtimes
- **WHEN** the draft has 13:00 and 18:00 events on one date at one venue
- **THEN** the Series has two DraftEvents
