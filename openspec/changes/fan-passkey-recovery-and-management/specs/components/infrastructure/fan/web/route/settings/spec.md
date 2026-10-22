## ADDED Requirements

### Requirement: Guest hero offers sign-in help

The guest call-to-action hero at the top of the Settings page SHALL show a "can't sign in" text link below its sign-in and sign-up actions that opens the passkey recovery screen.

#### Scenario: Guest opens sign-in help from Settings

- **WHEN** an unauthenticated user taps "can't sign in" in the Settings guest hero
- **THEN** the app navigates to `/passkey-recovery`

### Requirement: Passkey management requires a recent sign-in

For a signed-in fan, the ACCOUNT section SHALL show a Passkeys row that opens passkey management. Opening passkey management SHALL require that the fan signed in within the last 5 minutes; otherwise the app SHALL send the fan to the hosted login to sign in again with a passkey and SHALL return them to passkey management afterwards. The access gained this way SHALL last only while passkey management stays open: leaving it, or reloading the app, SHALL require the 5-minute rule again.

#### Scenario: Recent sign-in

- **WHEN** a fan who signed in 2 minutes ago opens the Passkeys row
- **THEN** passkey management opens directly

#### Scenario: Older sign-in

- **WHEN** a fan who signed in 3 days ago opens the Passkeys row
- **THEN** the hosted login asks for a passkey, and after it succeeds passkey management opens

#### Scenario: Re-opening after leaving

- **WHEN** the fan leaves passkey management and opens it again 6 minutes after signing in again
- **THEN** the hosted login asks for a passkey again

### Requirement: Passkey management lists, adds and removes passkeys

Passkey management SHALL list every passkey registered for the fan's identity, each with its name, or "Passkey" when it has none. It SHALL offer to add a passkey on the device in hand, which opens the hosted login to create it and returns to passkey management, where the new passkey is listed. Each listed passkey SHALL offer removal behind a confirmation that says the passkey is also kept by the device's passkey manager and should be deleted there too; after confirming, the passkey SHALL no longer be listed and SHALL no longer sign in. When only one passkey is listed, its removal SHALL be disabled with the explanation that the last passkey cannot be removed and that another passkey must be added first. When the list cannot be read or a removal fails, passkey management SHALL say so and offer to try again, and SHALL keep the list as it was.

#### Scenario: Two passkeys

- **WHEN** a fan with passkeys named `Apple iPhone, iOS, Mobile Safari` and `Windows, Chrome` opens passkey management
- **THEN** both are listed with those names and both offer removal

#### Scenario: Add a passkey on this device

- **WHEN** the fan taps add and creates a passkey on the device in hand
- **THEN** passkey management lists one more passkey

#### Scenario: Remove a passkey

- **WHEN** the fan removes `Windows, Chrome` and confirms
- **THEN** it is no longer listed and can no longer sign in to the account

#### Scenario: Last passkey

- **WHEN** only one passkey is listed
- **THEN** its removal is disabled and the explanation is shown

#### Scenario: Removal fails

- **WHEN** a removal fails
- **THEN** passkey management says so, offers to try again and still lists the passkey
