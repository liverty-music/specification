## ADDED Requirements

### Requirement: The conflict dialog says what each choice keeps

The conflict dialog's lede SHALL say that both choices keep one event and list the candidate's artist as one of its performers, except an Organizer's event, whose performers stay as they are, that Keep existing keeps the existing event's listed venue name and remembers the candidate's, that Adopt candidate shows the candidate's listed venue name and remembers the existing one, and that the candidate should be rejected instead when the two are not the same concert.

#### Scenario: Dialog explains the choices

- **WHEN** approval detects a duplicate and presents the conflict dialog
- **THEN** the lede states that either choice keeps one event with the candidate's artist as a performer (an Organizer's event keeps its performers), which listed venue name Keep existing and Adopt candidate each show, and that a different concert is to be rejected
