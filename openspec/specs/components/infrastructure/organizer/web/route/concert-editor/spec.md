# Concert Editor

## Purpose

The organizer console screen where an operator creates or edits a concert, including its cover image.

## Requirements

### Requirement: A new cover image is previewed while it is processed

After the operator picks a cover image, the editor SHALL show that image from the operator's device at once and SHALL say that the optimised image is still being processed. Once the processed image is available, the editor SHALL show it instead, without the operator reloading the editor. There is no processing status to wait for; the preview simply gives way to the processed image. Until then, saving the concert SHALL keep showing the picked image, never the previous cover: the concert page the save returns to SHALL show the picked image with the processing note, and SHALL show the processed image once it is available.

#### Scenario: Image just uploaded

- **WHEN** an operator picks a new cover image for a concert
- **THEN** the editor shows the picked image with a note that the optimised image is still being processed

#### Scenario: Processed image available

- **WHEN** the processed cover image becomes available while the editor is open
- **THEN** the editor shows the processed image and the note is gone

#### Scenario: Saved before processing finished

- **WHEN** an operator picks a new cover image for a concert that has a cover and saves before the new image is processed
- **THEN** the concert page opens and shows the picked image with the processing note, not the previous cover, until the processed image replaces it

### Requirement: A published concert is corrected, not rewritten

The editor SHALL show each event's publish state. For a PUBLISHED event it SHALL show the venue and date as fixed and offer no way to remove the event; a CANCELLED event SHALL be shown as 中止 (cancelled) and not be editable. Once the concert has a PUBLISHED or CANCELLED event, the type, source page and visibility SHALL be shown as fixed, and the performers SHALL stay editable. An event the operator adds to a published concert SHALL be saved as a draft and shown as such until it is published. When a save is refused because tickets for an event are already on sale and its start time was changed, the editor SHALL say that the start time is fixed once tickets are on sale.

#### Scenario: Published event's venue is fixed
- **WHEN** an operator edits a concert with a PUBLISHED event
- **THEN** that event's venue and date are shown as fixed and the event has no remove control

#### Scenario: Additional date saved as a draft
- **WHEN** an operator adds a date to a published concert and saves
- **THEN** the save succeeds and the new date is shown as a draft

#### Scenario: Start time already on sale
- **WHEN** an operator changes the start time of an event whose tickets are on sale and saves
- **THEN** the editor says the start time is fixed once tickets are on sale, and nothing is saved

### Requirement: The venue is found by search

For each event the editor SHALL offer a venue field that searches the map catalog as the operator types: 500 ms after the operator stops typing, once the text has at least 3 characters when it contains a Japanese character, or at least 5 characters otherwise, the field SHALL list up to 5 matching places with their name and address, and the operator picks one with the pointer or the keyboard. Only the results for the latest text SHALL be shown. The list SHALL credit Google Maps as the source. The editor SHALL never ask for a place id, and an event's venue SHALL be a picked place: a typed name alone is never saved. When nothing matches, the field SHALL say so and ask for another name. When the search is unavailable, the field SHALL say so and offer 再試行. The editor SHALL NOT save while an event has no picked place; the field in error SHALL say a venue must be picked from the results.

#### Scenario: Pick a venue

- **WHEN** an operator types Zepp Haneda and picks Zepp Haneda (TOKYO), 大田区羽田空港 from the list
- **THEN** the event's venue is that place and its name and address are shown in the field

#### Scenario: Short Japanese name

- **WHEN** an operator types 武道館 and pauses
- **THEN** the field lists matching places without any other action

#### Scenario: Short Latin text

- **WHEN** an operator types Zepp and pauses
- **THEN** no search runs until the text has 5 characters

#### Scenario: Typing on

- **WHEN** an operator types LIQUID, pauses, then types ROOM before the first results arrive
- **THEN** only the results for LIQUIDROOM are shown

#### Scenario: Keyboard pick

- **WHEN** the list is open and the operator presses the down arrow twice and Enter
- **THEN** the second place is picked and the list closes

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

### Requirement: Event times are entered in Japan time on a 24-hour clock

The editor SHALL take each event's date, open time and start time as Japan time, marked JST, whatever the device's time zone or language. Each time SHALL be entered as an hour from 00 to 23 and a minute in steps of 5, with no AM or PM. A new concert's first date SHALL start with 開場 (doors) 17:00 and 開演 (start) 19:00. Adding a date SHALL copy the previous date's venue, date, open time and start time into the new one.

#### Scenario: Device in another time zone

- **WHEN** an operator whose device is set to London time enters a start time of 18:00 JST and saves
- **THEN** the event starts at 18:00 Japan time, and reopening the editor shows 18:00 JST

#### Scenario: Device using a 12-hour clock

- **WHEN** an operator whose device shows times as 6:00 PM opens the editor
- **THEN** the time fields show hours 00 to 23 and no AM or PM

#### Scenario: Defaults of a new concert

- **WHEN** an operator creates a concert
- **THEN** its first date shows 開場 17:00 and 開演 19:00

#### Scenario: Another night at the same venue

- **WHEN** a date at Zepp Haneda on 3 November with 開場 17:00 and 開演 18:00 is followed by 日程を追加
- **THEN** the new date shows Zepp Haneda, 3 November, 17:00 and 18:00, ready to change the date

### Requirement: Save gives feedback and returns to where the editor was opened

Saving SHALL show progress in the save button and ignore repeated presses. A successful save SHALL return to the page the editor was opened from (the concert page; for a new concert, the new concert's page), which shows the saved values, and SHALL say so in the snackbar. A field error SHALL be shown next to the field and the first field in error SHALL receive focus. A failed save SHALL keep the editor open with everything the operator entered and offer 再試行 in the snackbar. Leaving without saving SHALL be offered as キャンセル (Cancel), and the editor SHALL guard unsaved changes when the operator leaves.

#### Scenario: Saved

- **WHEN** an operator opens the editor from the concert page, changes the description and saves
- **THEN** the concert page opens with the saved values and the snackbar says 変更を保存しました

#### Scenario: New concert

- **WHEN** an operator creates a new concert and saves
- **THEN** the new concert's page opens and the snackbar says it was created

#### Scenario: Missing performer

- **WHEN** an operator saves without a performer
- **THEN** the error is shown next to the performers and focus moves there

### Requirement: Visibility is chosen before publishing

The editor SHALL offer the concert's type as a choice of 単独公演 (single show), ツアー (tour) and フェス (festival), all visible at once, and its visibility as a choice of two, each with its effect: 公開 (PUBLIC: shown in fan lists, and followers are notified when it is published) and 限定公開 (UNLISTED: not shown in fan lists, and no follower is notified). A new concert SHALL start as 公開. Once the concert has a published or cancelled date, the visibility SHALL be shown as fixed.

#### Scenario: Unlisted concert created

- **WHEN** an operator creates a concert and chooses 限定公開
- **THEN** the concert is saved as UNLISTED, and publishing it later notifies no follower

#### Scenario: Visibility fixed after publish

- **WHEN** an operator edits a concert with a published date
- **THEN** the visibility is shown and cannot be changed
