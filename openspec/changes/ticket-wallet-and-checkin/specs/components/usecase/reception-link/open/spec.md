# Spec Delta

## Purpose

ReceptionLinkUseCase.Open is what a reception device does when staff open a link: it binds the link to that device's public key on first use, and tells the device whether it can scan now or when it can start.

## ADDED Requirements

### Requirement: The link binds to the first device

Open SHALL take a link token, the device's public key, a call signature with its signed time, and the current time. It SHALL find the link with ReceptionLink.GetByToken and bind it with ReceptionLink.BindDevice. It SHALL fail with PermissionDenied when no link holds the token or BindDevice reports Revoked, without telling the two apart, and with FailedPrecondition when BindDevice reports OtherDevice. After binding it SHALL fail with PermissionDenied when the call is not proven by the bound device, so a device must hold the private key of the public key it binds.

#### Scenario: Staff open the link for the first time

- **WHEN** an Unused link is opened on a device at 14:10
- **THEN** the link is bound to that device's public key and Open succeeds

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

On success Open SHALL return the link's name, the event's id and the reception window computed from Event.Get, and whether the current time is inside it. Opening outside the window SHALL still bind the link.

#### Scenario: Opened the day before

- **WHEN** the link is opened on 2026-11-19 for an event whose window opens at 2026-11-20 15:00
- **THEN** Open succeeds, reports the time outside the window and returns the opening 2026-11-20 15:00

#### Scenario: Opened during the window

- **WHEN** the link is opened at 16:00 inside the window
- **THEN** Open succeeds and reports the time inside the window
