# Spec Delta

## Purpose

The fan's tickets screen: the tickets issued to their account, each showing its 特定興行入場券 (covered ticket) face, and the entry QR code the device makes for the tickets entering together, which works without a connection at the venue.

## ADDED Requirements

### Requirement: Tickets grouped by event with their face

The screen SHALL list the signed-in fan's tickets grouped by event, nearest event first. Each ticket SHALL show its event's title, date, venue, open and start times, and its covered-ticket face: that resale without the organizer's consent is prohibited, the eligible person's name (the holder full name) and that no seat is assigned. Each ticket SHALL show its state: 未入場 (not yet entered), 入場済み (entered) with the admitted time, or 無効 (void). The last loaded list SHALL stay viewable without a connection.

#### Scenario: Fan opens their tickets

- **WHEN** a fan holding 3 tickets for one event opens the screen
- **THEN** the event is shown once with its 3 tickets, each with the resale notice, the holder name and 未入場

#### Scenario: Refunded ticket

- **WHEN** one of the fan's tickets was voided by a refund
- **THEN** it is shown as 無効 and offers no QR code

#### Scenario: No signal in the venue

- **WHEN** the fan opens the screen without a connection after loading it earlier
- **THEN** the tickets loaded earlier are shown

### Requirement: The device is prepared once while online

When the fan opens the screen with a connection and this device has no key pair registered for showing tickets, the screen SHALL create a key pair on the device, whose private key cannot be read out of the device by the page, and register its public key with WalletPublicKeyUseCase.Register. Registering SHALL ask nothing of the fan. The screen SHALL say that tickets are now shown from this device only, when the fan had shown tickets on another device before.

#### Scenario: First visit on a phone

- **WHEN** a fan opens the screen on a phone with a connection for the first time
- **THEN** the phone registers its key and can show the QR code offline from then on

#### Scenario: Not prepared and offline

- **WHEN** a fan opens the screen for the first time on a phone without a connection
- **THEN** the screen says it needs a connection once before the QR code can be shown

### Requirement: One QR code for the tickets entering together

For an event with tickets that are not yet entered, the screen SHALL offer to show the entry QR code. The code SHALL present every not-yet-entered ticket of the event, up to 10, unless the fan unticks some, and SHALL state how many people it admits. The device SHALL make a new code every 15 seconds while it is shown, signed with its private key, with or without a connection, and SHALL never show a code older than 15 seconds. While the code is shown the screen SHALL keep the display awake, and stop doing so when the code is closed. When no ticket is ticked, no code SHALL be shown.

#### Scenario: Whole group

- **WHEN** the fan shows the code for an event with 3 not-yet-entered tickets
- **THEN** one QR code stating 3名 is shown and it changes every 15 seconds

#### Scenario: Companion arrives later

- **WHEN** the fan unticks one ticket before showing the code
- **THEN** the code states 2名 and the unticked ticket stays 未入場 after the scan

#### Scenario: Shown without a connection

- **WHEN** the fan shows the code in the venue without a connection
- **THEN** the code is shown and changes every 15 seconds

#### Scenario: Screen stays on

- **WHEN** the code has been shown for 2 minutes without the fan touching the screen
- **THEN** the display has stayed on

#### Scenario: After entry

- **WHEN** the fan's tickets are admitted while the code is shown and the device has a connection
- **THEN** the screen shows them as 入場済み with the admitted time

### Requirement: Supported browsers

The screen, including making the QR code without a connection, SHALL work in the current and previous major versions of Safari on iOS and Chrome on Android.

#### Scenario: iPhone

- **WHEN** a fan opens the screen in Safari on an iPhone with the current iOS
- **THEN** the QR code can be shown
