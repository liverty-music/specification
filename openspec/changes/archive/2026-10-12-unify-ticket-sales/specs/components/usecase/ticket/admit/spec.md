# Spec Delta

## MODIFIED Requirements

### Requirement: Only a genuine, fresh code for this event

Admit SHALL read the scanned text with AdmissionCode.Decode; a Malformed text SHALL be rejected with reason Forged. It SHALL read the code's user's key with WalletPublicKey.GetByUser, rejecting with reason Forged when the user has none, and check the code with AdmissionCode.Verify at the current time: Forged is rejected with reason Forged, Expired with reason Expired. A code whose event is not the link's event SHALL be rejected with reason OtherEvent. Admit SHALL then read the code's user's Tickets for the event with Ticket.ListByUserAndEvent; when any presented Ticket is not among them, because it is another User's Ticket or it is for another event, the whole scan SHALL be rejected with reason Forged, since the tickets screen only ever presents the user's own Tickets of one event. In these cases no Ticket's admission SHALL be attempted.

#### Scenario: Screenshot shown later

- **WHEN** a QR code captured a minute earlier is scanned
- **THEN** the scan is rejected with reason Expired and no Ticket is admitted

#### Scenario: Code from a replaced phone

- **WHEN** a code made on the fan's old phone is scanned after the fan registered a new phone
- **THEN** the scan is rejected with reason Forged

#### Scenario: Not an entry code

- **WHEN** a QR code holding a web address is scanned
- **THEN** the scan is rejected with reason Forged

#### Scenario: Someone else's ticket

- **WHEN** a code signed with the user's key also presents a Ticket of another User
- **THEN** the whole scan is rejected with reason Forged and no Ticket is admitted

#### Scenario: Ticket of another event in the code

- **WHEN** a code for this event also presents one of the user's Tickets for another event
- **THEN** the whole scan is rejected with reason Forged and no Ticket is admitted

#### Scenario: Ticket for another event

- **WHEN** a genuine code for another event is scanned through this event's link
- **THEN** the scan is rejected with reason OtherEvent

### Requirement: The result carries no personal data

Admit SHALL return, for the scan, the number of Tickets admitted and, for each rejected Ticket or for the whole scan, the reason, with the earlier admit time and link number for AlreadyAdmitted. It SHALL NOT return the user's full name, phone number, account or any other personal data.

#### Scenario: Result of a group scan

- **WHEN** 2 Tickets are admitted and 1 is rejected as AlreadyAdmitted at 18:32 through `受付1`
- **THEN** the result says 2 admitted and 1 already admitted at 18:32 through `受付1`, and contains no name or phone number
