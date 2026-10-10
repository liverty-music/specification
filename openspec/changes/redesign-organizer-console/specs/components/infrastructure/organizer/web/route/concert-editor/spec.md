# Spec Delta

## ADDED Requirements

### Requirement: The venue is found by search

For each event the editor SHALL offer a venue field that searches the map catalog: the operator types a venue name and starts the search, the field lists up to 5 matching places with their name and address, and the operator picks one. The editor SHALL never ask for a place id. When nothing matches, the field SHALL say so and let the operator keep the typed name as the venue. When the search is unavailable, the field SHALL say so and keep the typed name.

#### Scenario: Pick a venue

- **WHEN** an operator types Zepp Haneda, searches and picks Zepp Haneda (TOKYO), 大田区羽田空港
- **THEN** the event's venue is that place and its name and address are shown in the field

#### Scenario: No match

- **WHEN** the search for a typed name finds no place
- **THEN** the field says no place was found and the typed name is kept as the venue

### Requirement: An unchanged venue is kept on save

Saving a concert SHALL keep the venue of every event whose venue the operator did not change, including the place it was matched to.

#### Scenario: Title change only

- **WHEN** an operator opens a concert whose event is at Zepp Haneda, changes only the title and saves
- **THEN** the event is still at the same Zepp Haneda venue

### Requirement: Event times are entered in Japan time

The editor SHALL take each event's date, start time and open time as Japan time, marked JST, whatever the device's time zone.

#### Scenario: Device in another time zone

- **WHEN** an operator whose device is set to London time enters a start time of 18:00 JST and saves
- **THEN** the event starts at 18:00 Japan time, and reopening the editor shows 18:00 JST

### Requirement: Save gives feedback and keeps the operator in place

Saving SHALL show progress in the save button and ignore repeated presses. A successful save of an existing concert SHALL say so in the snackbar and keep the editor open with the saved values; a successful save of a new concert SHALL open the new concert's page and say it was created. A field error SHALL be shown next to the field and the first field in error SHALL receive focus. A failed save SHALL keep everything the operator entered and offer 再試行 in the snackbar. The editor SHALL guard unsaved changes when the operator leaves.

#### Scenario: Saved

- **WHEN** an operator changes the description of an existing concert and saves
- **THEN** the snackbar says 変更を保存しました and the editor stays open

#### Scenario: New concert

- **WHEN** an operator creates a new concert and saves
- **THEN** the new concert's page opens and the snackbar says it was created

#### Scenario: Missing performer

- **WHEN** an operator saves without a performer
- **THEN** the error is shown next to the performers and focus moves there
