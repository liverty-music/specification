# Spec Delta

## Purpose

ScannerUseCase.Open is what a device does when venue staff open a Scanner's link: it binds the Scanner to that device's public key on first use, and tells the device whether it can scan now or when it can start.

## ADDED Requirements

### Requirement: The scanner binds to the first device

Open SHALL take a link token, the device's public key, a call signature with its signed time, and the current time. It SHALL find the Scanner with Scanner.GetByLinkToken and fail with PermissionDenied when no Scanner holds the link token. Before binding, it SHALL check that the call is proven by the given public key, and fail with PermissionDenied without binding when it is not, so a Scanner is only ever bound to a key whose private key the device holds. It SHALL then bind the Scanner with Scanner.BindDevice, failing with PermissionDenied when BindDevice reports Revoked, without telling it apart from an unknown link token, and with FailedPrecondition when BindDevice reports OtherDevice.

#### Scenario: Staff open the link for the first time

- **WHEN** the link of an Unused Scanner is opened on a device at 14:10
- **THEN** the Scanner is bound to that device's public key and Open succeeds

#### Scenario: Signature from another key

- **WHEN** the link of an Unused Scanner is opened with a public key and a signature made with a different private key
- **THEN** Open fails with PermissionDenied and the Scanner stays Unused

#### Scenario: Link forwarded to another device

- **WHEN** the link of a Scanner bound to one device is opened on another device
- **THEN** Open fails with FailedPrecondition and the Scanner stays bound to the first device

#### Scenario: Revoked scanner

- **WHEN** the link of a Revoked Scanner is opened
- **THEN** Open fails with PermissionDenied

#### Scenario: Unknown link token

- **WHEN** no Scanner holds the link token
- **THEN** Open fails with PermissionDenied

### Requirement: The device learns the admission window

On success Open SHALL return the Scanner's number, the event's id and the admission window computed from Event.Get, and whether the current time is inside it. Opening outside the window SHALL still bind the Scanner.

#### Scenario: Opened the day before

- **WHEN** the link is opened on 2026-11-19 for an event whose window opens at 2026-11-20 15:00
- **THEN** Open succeeds, reports the time outside the window and returns the opening 2026-11-20 15:00

#### Scenario: Opened during the window

- **WHEN** the link is opened at 16:00 inside the window
- **THEN** Open succeeds and reports the time inside the window
