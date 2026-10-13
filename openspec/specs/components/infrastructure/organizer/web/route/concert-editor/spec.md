# Concert Editor

## Purpose

The organizer console screen where an operator creates or edits a concert, including its cover image.

## Requirements

### Requirement: A new cover image is previewed while it is processed

After the operator picks a cover image, the editor SHALL show that image from the operator's device at once and SHALL say that the optimised image is still being processed. Once the processed image is available, the editor SHALL show it instead. There is no processing status to wait for; the preview simply gives way to the processed image.

#### Scenario: Image just uploaded

- **WHEN** an operator picks a new cover image for a concert
- **THEN** the editor shows the picked image with a note that the optimised image is still being processed

#### Scenario: Processed image available

- **WHEN** the processed cover image becomes available
- **THEN** the editor shows the processed image and the note is gone

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
