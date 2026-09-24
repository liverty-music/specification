## ADDED Requirements

### Requirement: Existing Passkey Capture Path Retained

The system SHALL retain the existing headed-Chromium passkey capture script (`capture-auth-state.ts`) unchanged. The password capture path SHALL NOT replace it.

**Rationale**: The passkey flow remains the canonical UX path under manual testing on display-capable hosts and exercises device-bound WebAuthn that the password path does not cover. Removing it would lose coverage and force every passkey-related issue to be debugged without a working test entry point.

#### Scenario: Passkey script still runnable on a display-capable host

- **WHEN** a developer on a host with a working display (non-WSL or WSL with x11 forwarding configured) runs the existing passkey capture script
- **THEN** the script SHALL behave exactly as before — open Chromium, drive the OIDC flow against the passkey-only user, write storage state to its existing output path
