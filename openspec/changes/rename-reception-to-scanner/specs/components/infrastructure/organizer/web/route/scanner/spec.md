# Spec Delta

## Purpose

The scanner screen venue staff open from a Scanner's link in the phone's browser: it scans fans' entry QR codes with the device camera and tells staff, without showing any personal data, whether to let the people in. It needs no sign-in, no app install and no scanner hardware.

## ADDED Requirements

### Requirement: Opened from the link without signing in

The screen SHALL open from a Scanner's link in the browser without asking for a sign-in or an install, reading the link token from the URL fragment. On first open the device SHALL create a key pair, whose private key cannot be read out of the device by the page, bind the Scanner to its public key with ScannerUseCase.Open, and sign every later call with the private key. The screen SHALL show the Scanner's label, for example 受付1. When a call is refused as not allowed (the link token is unknown, the Scanner is revoked, or the call is not proven, which also happens when the phone's clock is more than 30 seconds slow or 15 seconds fast), it SHALL say that the link can no longer be used, to check that the phone's clock is correct, and otherwise to ask the organizer for a new one; when the Scanner is bound to another device it SHALL say so and to ask the organizer to reissue it.

#### Scenario: Staff open the link

- **WHEN** venue staff open the link of `受付1` on a phone for the first time
- **THEN** the screen opens without a sign-in and shows `受付1`

#### Scenario: Forwarded link

- **WHEN** the link is opened on a second phone
- **THEN** the screen says the link is in use on another device and to ask the organizer to reissue it

#### Scenario: Revoked scanner

- **WHEN** the link of a revoked Scanner is opened
- **THEN** the screen says the link can no longer be used

#### Scenario: Phone clock far off

- **WHEN** the link is opened on a phone whose clock is 2 minutes slow
- **THEN** the screen says the link can no longer be used and to check the phone's clock

### Requirement: Scanning only during the admission window

Before the admission window the screen SHALL show when admission starts, after it SHALL show when admission ended, and when the event has no admission window it SHALL say that admission times are not set; in all three cases it SHALL not start the camera. Inside the window it SHALL ask for the rear camera only when staff start scanning, and scan continuously until they stop.

#### Scenario: Opened the day before

- **WHEN** the link is opened on the day before the event
- **THEN** the screen shows that admission starts at 2026-11-20 15:00 and the camera does not start

#### Scenario: Admission over

- **WHEN** the link is opened at 2026-11-21 05:00 for a window that closed at 2026-11-21 04:00
- **THEN** the screen shows that admission ended at 04:00 and the camera does not start

#### Scenario: Start scanning

- **WHEN** staff tap to start scanning inside the window
- **THEN** the rear camera starts and QR codes in view are scanned

### Requirement: The verdict without personal data

After each scan the screen SHALL show the verdict in large type with both colour and text: OK with the number of people to let in, or NG with the reason and what to do next. The reasons SHALL read: already used, with the time and Scanner label of the earlier admission; QR code expired, asking the fan to reopen the code; not a valid entry QR code, asking the fan to show it from the tickets screen on their registered phone; ticket for another event; and ticket no longer valid (refunded or resold). When a group is partly admitted, the screen SHALL show how many to let in and the reason for the rest. For 20 seconds after an OK, the screen SHALL not send another AdmissionCode of the same fan, so a fan whose phone renews the code while still in view is not shown NG for the people just let in. The screen SHALL never show a user's name, phone number or any other personal data.

#### Scenario: Group admitted

- **WHEN** a QR code for 3 people is scanned and all 3 are admitted
- **THEN** the screen shows OK and 3名 and no name

#### Scenario: Ticket used earlier

- **WHEN** a ticket admitted at 18:32 through `受付1` is scanned again
- **THEN** the screen shows NG, already used, 18:32 and `受付1`

#### Scenario: Code still in view after OK

- **WHEN** a fan's group was admitted and their phone stays in front of the camera while the code renews
- **THEN** the screen keeps showing OK and sends no further scan of that fan for 20 seconds

#### Scenario: Screenshot

- **WHEN** an expired QR code is scanned
- **THEN** the screen shows NG and asks the fan to reopen the code

### Requirement: Fail closed without a connection

When the server cannot be reached, the screen SHALL show that the scan was not decided and offer to scan again, and SHALL never show OK. While the code stays in view, it SHALL retry the undecided scan by itself, at most once every 3 seconds.

#### Scenario: Network down

- **WHEN** a scan cannot reach the server
- **THEN** the screen shows that the scan was not decided and offers a retry, and does not show OK

### Requirement: The staff guide is one tap away

The screen SHALL offer a link to the staff guide, a static page for venue staff with no prior knowledge: the steps of admitting fans, what each verdict means and what to tell the fan, and what to do when the screen cannot be used. The guide SHALL open in a new browser tab, so the screen keeps its state and its camera, and SHALL need no sign-in.

#### Scenario: Staff open the guide

- **WHEN** staff tap the link to the guide on the scanner screen
- **THEN** the guide opens in a new tab without a sign-in and the scanner screen stays as it was

### Requirement: Supported browsers

The screen SHALL work in a browser tab of the current and previous major versions of Safari on iOS and Chrome on Android, on phones with a rear camera.

#### Scenario: Staff iPhone

- **WHEN** staff open the link in Safari on an iPhone with the current iOS
- **THEN** QR codes can be scanned
