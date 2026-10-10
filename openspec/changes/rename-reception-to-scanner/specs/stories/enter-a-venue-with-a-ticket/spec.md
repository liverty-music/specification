# Spec Delta

## MODIFIED Requirements

### Requirement: Fan and companions enter together

After an Organizer creates a Scanner with ScannerUseCase.Create and venue staff open its link on a device with ScannerUseCase.Open, a fan whose phone registered its key with WalletPublicKeyUseCase.Register and who holds Issued tickets for the event SHALL be able to show the QR code their phone makes and be admitted with TicketUseCase.Admit during the admission window; their tickets SHALL then be shown as entered in TicketUseCase.GetMyTickets.

#### Scenario: Group of three enters

- **WHEN** a fan holding 3 tickets shows their QR code to `受付1` at 18:32 inside the window
- **THEN** staff see OK and 3名 without any name, and the fan's 3 tickets show as entered at 18:32

#### Scenario: No signal in the venue

- **WHEN** the fan's phone has no connection in the venue but registered its key earlier
- **THEN** the fan still shows the QR code and is admitted

### Requirement: A ticket admits only once

A ticket that has been admitted SHALL be refused at every later scan, through any Scanner, and staff SHALL see when and through which Scanner it was admitted.

#### Scenario: Same code at two entrances

- **WHEN** the same QR code is scanned at `受付1` and `受付2` at the same moment
- **THEN** its tickets are admitted once in total, and the other entrance sees NG, already used, with the time and Scanner label

### Requirement: Only the bound device, only during the window

A Scanner SHALL admit only from the device that first opened its link, only during the event's admission window, and not at all once the Organizer has revoked it.

#### Scenario: Link forwarded

- **WHEN** staff forward the link of `受付1` to another phone and scan there
- **THEN** that phone is refused and the fan is not admitted

#### Scenario: Lost phone revoked

- **WHEN** the Organizer revokes and reissues `受付1` after the phone is lost
- **THEN** the lost phone can no longer admit, and the reissued Scanner works on the replacement phone
