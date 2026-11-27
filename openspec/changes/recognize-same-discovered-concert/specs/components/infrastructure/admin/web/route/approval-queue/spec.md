## ADDED Requirements

### Requirement: The conflict dialog says what each choice keeps

The conflict dialog's lede SHALL say that both choices keep one event and list the candidate's artist as one of its performers, except an Organizer's event, whose performers, listed venue name and times stay as they are and which only Keep existing applies to, that Keep existing keeps the existing event's listed venue name and remembers the candidate's, that Adopt candidate shows the candidate's listed venue name and remembers the existing one, and that the candidate should be rejected instead when the two are not the same concert.

#### Scenario: Dialog explains the choices

- **WHEN** approval detects a duplicate and presents the conflict dialog
- **THEN** the lede states that either choice keeps one event with the candidate's artist as a performer (an Organizer's event keeps its performers and only Keep existing applies to it), which listed venue name Keep existing and Adopt candidate each show, and that a different concert is to be rejected

### Requirement: Adopt refused for an Organizer's event

When Approve refuses adopt the candidate with FailedPrecondition (the existing event is an Organizer's), the conflict dialog SHALL stay open with the row kept in the queue and SHALL say that the event keeps its listed venue name and times and that Keep existing or rejecting the candidate remains.

#### Scenario: Adopt refused
- **WHEN** the admin chooses Adopt candidate and Approve fails with FailedPrecondition
- **THEN** the dialog stays open, says to choose Keep existing or reject the candidate, and the row stays in the queue
