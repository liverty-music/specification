# Spec Delta

## MODIFIED Requirements

### Requirement: Every ticket is a covered ticket

Every Ticket SHALL carry the three conditions of a 特定興行入場券 (covered ticket): its face states that resale without the organizer's consent is prohibited; it names the event (date and venue) and the eligible person, who is the Ticket's user, with no seat assigned; and it shows the user's full name and phone number as the User currently records them (本人確認, identity check).

#### Scenario: Issued ticket face
- **WHEN** a Ticket is issued
- **THEN** it states that resale without consent is prohibited, names its event and its user, shows the user's full name and phone number, and has no seat

#### Scenario: User corrects their details
- **WHEN** the Ticket's user changes their phone number
- **THEN** the Ticket's face shows the new phone number

#### Scenario: Resale flag cannot be false
- **WHEN** a Ticket states resale without consent is not prohibited
- **THEN** the Ticket is invalid
