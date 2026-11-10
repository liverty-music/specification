## ADDED Requirements

### Requirement: Dialogs and disclosures move when they open and close

A confirmation dialog SHALL fade in when it opens and fade out when it closes, over the app's short motion duration, and SHALL stay on top of the page until the fade-out ends. A disclosure (a section the fan opens to read more, such as an OSS license text) SHALL grow to its content's height when opened and shrink when closed, where the browser can animate to a content height; elsewhere it SHALL open and close at once. Under reduced motion both SHALL open and close at once.

#### Scenario: Confirmation dialog closes

- **WHEN** the fan answers a confirmation dialog
- **THEN** the dialog fades out and stays above the page until it is fully transparent

#### Scenario: License text opens

- **WHEN** the fan opens a license text in a browser that can animate to a content height
- **THEN** the section grows from closed to the height of the text

#### Scenario: Reduced motion

- **WHEN** the fan has asked the system for reduced motion and closes a confirmation dialog
- **THEN** the dialog disappears at once
