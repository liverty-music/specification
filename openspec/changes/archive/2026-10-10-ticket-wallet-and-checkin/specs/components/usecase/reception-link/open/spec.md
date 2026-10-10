# Spec Delta

## Purpose

ReceptionLinkUseCase.Open is what a reception device does when staff open a link: it binds the link to that device's public key on first use, and tells the device whether it can scan now or when it can start.

## ADDED Requirements

### Requirement: The link binds to the first device

Open SHALL take a link token, the device's public key, a call signature with its signed time, and the current time. It SHALL find the link with ReceptionLink.GetByToken and fail with PermissionDenied when no link holds the token. Before binding, it SHALL check that the call is proven by the given public key, and fail with PermissionDenied without binding when it is not, so a link is only ever bound to a key whose private key the device holds. It SHALL then bind the link with ReceptionLink.BindDevice, failing with PermissionDenied when BindDevice reports Revoked, without telling it apart from an unknown token, and with FailedPrecondition when BindDevice reports OtherDevice.

#### Scenario: Staff open the link for the first time

- **WHEN** an Unused link is opened on a device at 14:10
- **THEN** the link is bound to that device's public key and Open succeeds

#### Scenario: Signature from another key

- **WHEN** an Unused link is opened with a public key and a signature made with a different private key
- **THEN** Open fails with PermissionDenied and the link stays Unused

#### Scenario: Link forwarded to another device

- **WHEN** a link bound to one device is opened on another device
- **THEN** Open fails with FailedPrecondition and the link stays bound to the first device

#### Scenario: Revoked link

- **WHEN** a Revoked link is opened
- **THEN** Open fails with PermissionDenied

#### Scenario: Unknown token

- **WHEN** no link holds the token
- **THEN** Open fails with PermissionDenied

### Requirement: The device learns the window

On success Open SHALL return the link's number, the event's id and the reception window computed from Event.Get, and whether the current time is inside it. Opening outside the window SHALL still bind the link.

#### Scenario: Opened the day before

- **WHEN** the link is opened on 2026-11-19 for an event whose window opens at 2026-11-20 15:00
- **THEN** Open succeeds, reports the time outside the window and returns the opening 2026-11-20 15:00

#### Scenario: Opened during the window

- **WHEN** the link is opened at 16:00 inside the window
- **THEN** Open succeeds and reports the time inside the window
