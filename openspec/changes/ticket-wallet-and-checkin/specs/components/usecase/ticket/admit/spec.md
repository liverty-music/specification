# Spec Delta

## Purpose

TicketUseCase.Admit decides one scan at the venue: through a ReceptionLink, from the device it is bound to, during its event's reception window, it admits each Ticket a genuine and fresh AdmissionCode presents exactly once, records every outcome, and tells staff the result without any personal data.

## ADDED Requirements

### Requirement: Only the bound device, through a usable link, during the window

Admit SHALL take a link token, a call signature with its signed time, the scanned text and the current time. It SHALL find the link with ReceptionLink.GetByToken and fail with PermissionDenied when no link holds the token, when the link is Revoked, or when the call is not proven by the link's bound device. It SHALL read the link's event with Event.Get and fail with FailedPrecondition, recording nothing, when the current time is outside the link's reception window. A link revoked while a scan is being decided SHALL be treated as Revoked.

#### Scenario: Revoked link

- **WHEN** a scan arrives through a Revoked link
- **THEN** Admit fails with PermissionDenied and no Ticket is admitted

#### Scenario: Call from another device

- **WHEN** a scan arrives signed by a device other than the one the link is bound to
- **THEN** Admit fails with PermissionDenied and no Ticket is admitted

#### Scenario: After the window

- **WHEN** a scan arrives at 04:30 the day after the event
- **THEN** Admit fails with FailedPrecondition and nothing is recorded

### Requirement: Only a genuine, fresh code for this event

Admit SHALL read the scanned text with AdmissionCode.Decode; a Malformed text SHALL be rejected with reason Forged. It SHALL read the code's user's key with WalletPublicKey.GetActiveByUser, rejecting with reason Forged when the user has none, and check the code with AdmissionCode.Verify at the current time: Forged is rejected with reason Forged, Expired with reason Expired. A code whose event is not the link's event SHALL be rejected with reason OtherEvent. In these cases no Ticket's admission SHALL be attempted.

#### Scenario: Screenshot shown later

- **WHEN** a QR code captured a minute earlier is scanned
- **THEN** the scan is rejected with reason Expired and no Ticket is admitted

#### Scenario: Code from a replaced phone

- **WHEN** a code made on the fan's old phone is scanned after the fan registered a new phone
- **THEN** the scan is rejected with reason Forged

#### Scenario: Not an entry code

- **WHEN** a QR code holding a web address is scanned
- **THEN** the scan is rejected with reason Forged

#### Scenario: Ticket for another event

- **WHEN** a genuine code for another event is scanned through this event's link
- **THEN** the scan is rejected with reason OtherEvent

### Requirement: Each presented ticket admitted exactly once

For a genuine, fresh code for the link's event, Admit SHALL decide each presented Ticket independently, so a group can be partly admitted. It SHALL read the code's user's Tickets for the event with Ticket.ListByHolderAndEvent; a presented Ticket that is not among them SHALL be rejected with reason NotHolder. Otherwise Admit SHALL call Ticket.Admit with the link and the current time: a Ticket reported Admitted is admitted; one reported AlreadyAdmitted is rejected with reason AlreadyAdmitted, together with the time and link name read with AdmissionRecord.GetAdmissionByTicket; one reported Voided is rejected with reason Voided.

#### Scenario: Group of three admitted

- **WHEN** a code presenting 3 admissible Tickets is scanned
- **THEN** all 3 are admitted

#### Scenario: Same code at two entrances

- **WHEN** the same code is scanned through `受付A` and `受付B` at the same time
- **THEN** each Ticket is admitted through exactly one of them and rejected with reason AlreadyAdmitted through the other

#### Scenario: Already used earlier

- **WHEN** a Ticket admitted at 18:32 through `受付A` is presented again
- **THEN** it is rejected with reason AlreadyAdmitted, 18:32 and `受付A`

#### Scenario: Someone else's ticket

- **WHEN** a fan's genuine code presents a Ticket held by another account
- **THEN** that Ticket is rejected with reason NotHolder and the fan's own Tickets in the code are decided as usual

#### Scenario: Refunded ticket

- **WHEN** a code presents a Ticket that was Voided by a refund
- **THEN** the Ticket is rejected with reason Voided

### Requirement: Every outcome recorded

Each admission SHALL be recorded by Ticket.Admit itself. Admit SHALL append every rejection with AdmissionRecord.Append: one Rejected record per rejected Ticket, and one Rejected record without a Ticket for a scan rejected as Forged, each naming the link and the current time. When appending a rejection fails, Admit SHALL still return the result; when Ticket.Admit fails, Admit SHALL fail with Unavailable and staff scan again, and a Ticket admitted before the failure is reported AlreadyAdmitted on that next scan.

#### Scenario: Admission recorded

- **WHEN** a Ticket is admitted through `受付A` at 18:32
- **THEN** an Admitted record with that Ticket, `受付A` and 18:32 is stored

#### Scenario: Rejection recorded

- **WHEN** the same Ticket is presented again at 18:40
- **THEN** a Rejected record with reason AlreadyAdmitted, `受付A` and 18:40 is stored and the 18:32 record is unchanged

### Requirement: The result carries no personal data

Admit SHALL return, for the scan, the number of Tickets admitted and, for each rejected Ticket or for the whole scan, the reason, with the earlier admission time and link name for AlreadyAdmitted. It SHALL NOT return the holder's name, phone number, account or any other personal data.

#### Scenario: Result of a group scan

- **WHEN** 2 Tickets are admitted and 1 is rejected as AlreadyAdmitted at 18:32 through `受付A`
- **THEN** the result says 2 admitted and 1 already admitted at 18:32 through `受付A`, and contains no name or phone number
