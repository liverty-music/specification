# Spec Delta

## MODIFIED Requirements

### Requirement: The link token and the device's signature are the caller

Open and Admit SHALL accept a call that carries no sign-in. Every call SHALL carry a link token, a sign time and a signature over the link token, the call's content and the sign time; Open SHALL also carry the device's public key. A call missing any of them SHALL fail with InvalidArgument before any usecase runs, as SHALL an Admit call without scanned text. The boundary SHALL pass them, with the current time, to ScannerUseCase.Open or TicketUseCase.Admit, which decide whether the Scanner and the device are allowed.

#### Scenario: Staff device without an account

- **WHEN** a device with no sign-in calls Open with a valid link token, its public key and a signature
- **THEN** the call reaches ScannerUseCase.Open

#### Scenario: Missing signature

- **WHEN** Admit is called without a signature
- **THEN** it fails with InvalidArgument and nothing is admitted
