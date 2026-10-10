# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: Only the bound device, through a usable link, during the window`
- TO: `### Requirement: Only the bound device of a usable scanner, during the admission window`

## MODIFIED Requirements

### Requirement: Only the bound device of a usable scanner, during the admission window

Admit SHALL take a link token, a call signature with its signed time, the scanned text and the current time. It SHALL find the Scanner with Scanner.GetByLinkToken and fail with PermissionDenied when no Scanner holds the link token, when the Scanner is Revoked, or when the call is not proven by the Scanner's bound device. It SHALL read the Scanner's event with Event.Get and fail with FailedPrecondition, recording nothing, when the current time is outside the Scanner's admission window. A Scanner revoked while a scan is being decided SHALL be treated as Revoked: Admit fails with PermissionDenied, and Tickets of the scan admitted before the revocation stay admitted and are reported AlreadyAdmitted on a later scan.

#### Scenario: Revoked link

- **WHEN** a scan arrives through a Revoked Scanner
- **THEN** Admit fails with PermissionDenied and no Ticket is admitted

#### Scenario: Call from another device

- **WHEN** a scan arrives signed by a device other than the one the Scanner is bound to
- **THEN** Admit fails with PermissionDenied and no Ticket is admitted

#### Scenario: Revoked during a group scan

- **WHEN** a Scanner is revoked after the first of 3 Tickets in a scan was admitted
- **THEN** Admit fails with PermissionDenied, the first Ticket stays admitted, and on a later scan it is rejected with reason AlreadyAdmitted

#### Scenario: After the window

- **WHEN** a scan arrives at 04:30 the day after the event
- **THEN** Admit fails with FailedPrecondition and nothing is recorded

### Requirement: Only a genuine, fresh code for this event

Admit SHALL read the scanned text with AdmissionCode.Decode; a Malformed text SHALL be rejected with reason Forged. It SHALL read the code's user's key with WalletPublicKey.GetByUser, rejecting with reason Forged when the user has none, and check the code with AdmissionCode.Verify at the current time: Forged is rejected with reason Forged, Expired with reason Expired. A code whose event is not the Scanner's event SHALL be rejected with reason OtherEvent. Admit SHALL then read the code's user's Tickets for the event with Ticket.ListByUserAndEvent; when any presented Ticket is not among them, because it is another User's Ticket or it is for another event, the whole scan SHALL be rejected with reason Forged, since the tickets screen only ever presents the user's own Tickets of one event. In these cases no Ticket's admission SHALL be attempted.

#### Scenario: Screenshot shown later

- **WHEN** a QR code captured a minute earlier is scanned
- **THEN** the scan is rejected with reason Expired and no Ticket is admitted

#### Scenario: Code from a replaced phone

- **WHEN** an AdmissionCode made on the fan's old phone is scanned after the fan registered a new phone
- **THEN** the scan is rejected with reason Forged

#### Scenario: Not an entry code

- **WHEN** a QR code holding a web address is scanned
- **THEN** the scan is rejected with reason Forged

#### Scenario: Someone else's ticket

- **WHEN** an AdmissionCode signed with the user's key also presents a Ticket of another User
- **THEN** the whole scan is rejected with reason Forged and no Ticket is admitted

#### Scenario: Ticket of another event in the code

- **WHEN** an AdmissionCode for this event also presents one of the user's Tickets for another event
- **THEN** the whole scan is rejected with reason Forged and no Ticket is admitted

#### Scenario: Ticket for another event

- **WHEN** a genuine AdmissionCode for another event is scanned through this event's Scanner
- **THEN** the scan is rejected with reason OtherEvent

### Requirement: Each presented ticket admitted exactly once

For a genuine, fresh code for the Scanner's event whose Tickets are all the user's own, Admit SHALL decide each presented Ticket independently, so a group can be partly admitted. Admit SHALL call Ticket.Admit with the Scanner and the current time: a Ticket reported Admitted is admitted; one reported AlreadyAdmitted is rejected with reason AlreadyAdmitted, together with its admitted time and the Scanner number read with Admission.GetByTicket, or the admitted time alone when that read fails; one reported Voided is rejected with reason Voided.

#### Scenario: Group of three admitted

- **WHEN** an AdmissionCode presenting 3 admissible Tickets is scanned
- **THEN** all 3 are admitted

#### Scenario: Same code at two entrances

- **WHEN** the same AdmissionCode is scanned through `受付1` and `受付2` at the same time
- **THEN** each Ticket is admitted through exactly one of them and rejected with reason AlreadyAdmitted through the other

#### Scenario: Already used earlier

- **WHEN** a Ticket admitted at 18:32 through `受付1` is presented again
- **THEN** it is rejected with reason AlreadyAdmitted, 18:32 and `受付1`

#### Scenario: Refunded ticket

- **WHEN** an AdmissionCode presents a Ticket that was Voided by a refund
- **THEN** the Ticket is rejected with reason Voided

### Requirement: Every outcome recorded

Each Admission SHALL be stored by Ticket.Admit itself. Admit SHALL append every refusal with RejectedScan.Append, each naming the Scanner and the current time: one RejectedScan without a Ticket for a scan rejected as Forged; one per presented Ticket for a scan rejected as Expired or OtherEvent; and one per rejected Ticket otherwise. When appending a rejection fails, Admit SHALL still return the result; when Ticket.Admit fails, Admit SHALL fail with Unavailable and staff scan again, and a Ticket admitted before the failure is reported AlreadyAdmitted on that next scan.

#### Scenario: Admission recorded

- **WHEN** a Ticket is admitted through `受付1` at 18:32
- **THEN** an Admission with that Ticket, `受付1` and 18:32 is stored

#### Scenario: Rejection recorded

- **WHEN** the same Ticket is presented again at 18:40
- **THEN** a RejectedScan with reason AlreadyAdmitted, `受付1` and 18:40 is stored and the 18:32 Admission is unchanged

### Requirement: The result carries no personal data

Admit SHALL return, for the scan, the number of Tickets admitted and, for each rejected Ticket or for the whole scan, the reason, with the earlier admission time and Scanner number for AlreadyAdmitted. It SHALL NOT return the user's name, phone number, account or any other personal data.

#### Scenario: Result of a group scan

- **WHEN** 2 Tickets are admitted and 1 is rejected as AlreadyAdmitted at 18:32 through `受付1`
- **THEN** the result says 2 admitted and 1 already admitted at 18:32 through `受付1`, and contains no name or phone number
