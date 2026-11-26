## ADDED Requirements

### Requirement: Content that loads shows a skeleton and fades in

While a screen or a section of it waits for data to show, it SHALL show grey placeholder shapes in the positions, and with the sizes, of the content that will replace them (a skeleton), instead of only a line of loading text or an empty area. The skeleton SHALL take the same space as the loaded content so that the layout does not move when the content arrives; where the loaded height follows the data (the number of entries, the steps of a form), the skeleton uses the shared placeholder row sizes and a small layout move is accepted. While earlier results are still on screen (a search being refined), they stay and no skeleton is added. When the content arrives it SHALL fade in over the skeleton's place, and lists and grids SHALL fade in row by row rather than all at once. A skeleton SHALL NOT be used for a wait the fan started on purpose and for which a progress indicator already exists (a payment being confirmed, a file being sent). Under reduced motion the skeleton SHALL be still, and the content SHALL replace it through a fade of 100 ms or less.

#### Scenario: List loads

- **WHEN** the fan opens a list screen whose data takes 600 ms to arrive
- **THEN** placeholder rows of the same height as the loaded rows are shown while the data is pending
- **AND** the loaded rows fade in row by row, with no movement of the rows below or above them

#### Scenario: Reduced motion

- **WHEN** the fan has asked the system for reduced motion and a skeleton is shown
- **THEN** the skeleton does not animate
- **AND** the content replaces it through a fade of 100 ms or less

### Requirement: The text field caret takes the primary colour

The caret of the shared text field SHALL take the `primary` colour role, and the `error` role while the field is invalid, as the M3 outlined text field caret tokens state.

#### Scenario: Text field caret

- **WHEN** the fan focuses a text field
- **THEN** its caret is drawn in the `primary` colour

## MODIFIED Requirements

### Requirement: Dialogs and disclosures move when they open and close

A confirmation dialog SHALL fade in when it opens and fade out when it closes, over the app's short motion duration, and SHALL stay on top of the page until the fade-out ends. A disclosure (a section the fan opens to read more, such as an OSS license text) SHALL grow to its content's height when opened and shrink when closed, where the browser can animate to a content height; elsewhere it SHALL open and close at once. Under reduced motion a confirmation dialog SHALL open and close through a fade of 100 ms or less, and a disclosure SHALL open and close at once.

#### Scenario: Confirmation dialog closes

- **WHEN** the fan answers a confirmation dialog
- **THEN** the dialog fades out and stays above the page until it is fully transparent

#### Scenario: License text opens

- **WHEN** the fan opens a license text in a browser that can animate to a content height
- **THEN** the section grows from closed to the height of the text

#### Scenario: Reduced motion

- **WHEN** the fan has asked the system for reduced motion and closes a confirmation dialog
- **THEN** the dialog fades out within 100 ms and does not move
- **AND** a disclosure the fan opens or closes does so at once
