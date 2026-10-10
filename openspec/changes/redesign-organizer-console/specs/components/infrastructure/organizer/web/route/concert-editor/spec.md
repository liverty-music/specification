# Spec Delta

## ADDED Requirements

### Requirement: The venue is found by search

For each event the editor SHALL offer a venue field that searches the map catalog: the operator types a venue name and starts the search, the field lists up to 5 matching places with their name and address, and the operator picks one. The editor SHALL never ask for a place id, and an event's venue SHALL be a picked place: a typed name alone is never saved. When nothing matches, the field SHALL say so and ask for another name. When the search is unavailable, the field SHALL say so and offer 再試行. The editor SHALL NOT save while an event has no picked place; the field in error SHALL say a venue must be picked from the results.

#### Scenario: Pick a venue

- **WHEN** an operator types Zepp Haneda, searches and picks Zepp Haneda (TOKYO), 大田区羽田空港
- **THEN** the event's venue is that place and its name and address are shown in the field

#### Scenario: No match

- **WHEN** the search for a typed name finds no place
- **THEN** the field says no place was found and asks for another name, and the event has no venue

#### Scenario: Search unavailable

- **WHEN** the map catalog cannot be reached during a search
- **THEN** the field says the search is unavailable and offers 再試行, and the event has no venue

#### Scenario: Typed name not picked

- **WHEN** an operator types a venue name, does not pick a result and saves
- **THEN** nothing is saved, the venue field says a venue must be picked from the results, and focus moves there

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

## MODIFIED Requirements

### Requirement: A new cover image is previewed while it is processed

After the operator picks a cover image, the editor SHALL show that image from the operator's device at once and SHALL say that the optimised image is still being processed. Once the processed image is available, the editor SHALL show it instead, without the operator reloading the editor. There is no processing status to wait for; the preview simply gives way to the processed image. Until then, saving the concert SHALL keep showing the picked image, never the previous cover.

#### Scenario: Image just uploaded

- **WHEN** an operator picks a new cover image for a concert
- **THEN** the editor shows the picked image with a note that the optimised image is still being processed

#### Scenario: Processed image available

- **WHEN** the processed cover image becomes available while the editor is open
- **THEN** the editor shows the processed image and the note is gone

#### Scenario: Saved before processing finished

- **WHEN** an operator picks a new cover image for a concert that has a cover and saves before the new image is processed
- **THEN** the editor still shows the picked image with the processing note, not the previous cover

