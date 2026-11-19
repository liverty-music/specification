# Spec Delta

## MODIFIED Requirements

### Requirement: Only the bound device of a usable scanner, during the admission window

Admit SHALL take a link token, a call signature with its sign time, the scanned text and the current time. It SHALL find the Scanner with Scanner.GetByLinkToken and fail with PermissionDenied when no Scanner holds the link token, when the Scanner is Revoked, or when the call is not proven by the Scanner's bound device. It SHALL read the Scanner's event with Event.Get and fail with FailedPrecondition, recording nothing, when the current time is outside the Scanner's admission window. A Scanner revoked while a scan is being decided SHALL be treated as Revoked: Admit fails with PermissionDenied, and Tickets of the scan admitted before the revocation stay admitted and are reported AlreadyAdmitted on a later scan.

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
