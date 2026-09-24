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
