# Spec Delta

## Purpose

The reception screen venue staff open from a ReceptionLink in the phone's browser: it scans fans' QR codes with the device camera and tells staff, without showing any personal data, whether to let the people in. It needs no sign-in, no app install and no scanner hardware.

## ADDED Requirements

### Requirement: Opened from the link without signing in

The screen SHALL open from a ReceptionLink URL in the browser without asking for a sign-in or an install. On first open the device SHALL create a key pair, whose private key cannot be read out of the device by the page, bind the link to its public key with ReceptionLinkUseCase.Open, and sign every later call with the private key. The screen SHALL show the link's name. When the link is unknown or revoked it SHALL say that the link can no longer be used and to ask the organizer for a new one; when the link is bound to another device it SHALL say so and to ask the organizer to reissue it.

#### Scenario: Staff open the link

- **WHEN** venue staff open the link `受付A` on a phone for the first time
- **THEN** the screen opens without a sign-in and shows `受付A`

#### Scenario: Forwarded link

- **WHEN** the link is opened on a second phone
- **THEN** the screen says the link is in use on another device and to ask the organizer to reissue it

#### Scenario: Revoked link

- **WHEN** a revoked link is opened
- **THEN** the screen says the link can no longer be used

### Requirement: Scanning only during the reception window

Outside the reception window the screen SHALL show when reception starts and SHALL not start the camera. Inside the window it SHALL ask for the rear camera only when staff start scanning, and scan continuously until they stop.

#### Scenario: Opened the day before

- **WHEN** the link is opened on the day before the event
- **THEN** the screen shows that reception starts at 2026-11-20 15:00 and the camera does not start

#### Scenario: Start scanning

- **WHEN** staff tap to start scanning inside the window
- **THEN** the rear camera starts and QR codes in view are scanned

### Requirement: The verdict without personal data

After each scan the screen SHALL show the verdict in large type with both colour and text: OK with the number of people to let in, or NG with the reason and what to do next. The reasons SHALL read: already used, with the time and link name of the earlier admission; QR code expired, asking the fan to reopen the code; not a valid entry code, asking the fan to show it from the tickets screen on their registered phone; ticket for another event; ticket of another person; and ticket no longer valid (refunded or resold). When a group is partly admitted, the screen SHALL show how many to let in and the reason for the rest. The screen SHALL never show a holder's name, phone number or any other personal data.

#### Scenario: Group admitted

- **WHEN** a QR code for 3 people is scanned and all 3 are admitted
- **THEN** the screen shows OK and 3名 and no name

#### Scenario: Ticket used earlier

- **WHEN** a ticket admitted at 18:32 through `受付A` is scanned again
- **THEN** the screen shows NG, already used, 18:32 and `受付A`

#### Scenario: Screenshot

- **WHEN** an expired QR code is scanned
- **THEN** the screen shows NG and asks the fan to reopen the code

### Requirement: Fail closed without a connection

When the server cannot be reached, the screen SHALL show that the scan was not decided and offer to scan again, and SHALL never show OK.

#### Scenario: Network down

- **WHEN** a scan cannot reach the server
- **THEN** the screen shows that the scan was not decided and offers a retry, and does not show OK

### Requirement: Supported browsers

The screen SHALL work in a browser tab of the current and previous major versions of Safari on iOS and Chrome on Android, on phones with a rear camera.

#### Scenario: Staff iPhone

- **WHEN** staff open the link in Safari on an iPhone with the current iOS
- **THEN** QR codes can be scanned
