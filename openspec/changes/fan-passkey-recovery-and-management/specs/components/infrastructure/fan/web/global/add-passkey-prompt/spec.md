## Purpose

Offers a fan who just logged in on a device that may hold none of their passkeys (for example after signing in with a phone by scanning a QR code) to create a passkey on that device, so the device signs in with its own passkey next time.

## ADDED Requirements

### Requirement: The prompt follows a Log In on a device without a passkey record

The app SHALL keep, on each device, a record that a passkey was created or confirmed on that device. The record SHALL be set when the fan signs up on the device, adds a passkey on the device from passkey management or from the prompt, or chooses "This device already has one". After a Log In (not a sign-up) on a device without the record, the app SHALL show the add-passkey prompt once, unless the fan chose "Later" on that device within the last 30 days. While the prompt is shown, no other prompt SHALL open.

#### Scenario: Log In with another device's passkey

- **WHEN** a fan logs in on a laptop that has no record, by scanning a QR code with their phone
- **THEN** the add-passkey prompt is shown

#### Scenario: Device that already has the record

- **WHEN** a fan logs in on a device where they signed up
- **THEN** the add-passkey prompt is not shown

#### Scenario: Later chosen recently

- **WHEN** the fan chose "Later" on the device 10 days ago and logs in again there
- **THEN** the add-passkey prompt is not shown

#### Scenario: Later chosen long ago

- **WHEN** the fan chose "Later" on the device 31 days ago and logs in again there
- **THEN** the add-passkey prompt is shown

### Requirement: The prompt offers three choices

The add-passkey prompt SHALL offer "Create a passkey on this device", "This device already has one" and "Later", and SHALL be dismissible, which counts as "Later". "Create a passkey on this device" SHALL open the hosted login to create a passkey on the device and SHALL return the fan to the screen they were on. "This device already has one" SHALL set the device's record and close the prompt.

#### Scenario: Create on this device

- **WHEN** the fan chooses "Create a passkey on this device" and creates the passkey
- **THEN** the fan returns to the screen they were on, the device's record is set and the prompt is not shown after later Log Ins on the device

#### Scenario: Already has one

- **WHEN** the fan chooses "This device already has one"
- **THEN** the prompt closes and is not shown after later Log Ins on the device

#### Scenario: Dismissed

- **WHEN** the fan dismisses the prompt
- **THEN** it is not shown again on that device for 30 days
