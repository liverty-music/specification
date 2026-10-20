## ADDED Requirements

### Requirement: Dismissed notification prompt does not reappear

When the user dismisses the notification prompt, the system SHALL persist the dismissal and SHALL NOT show that prompt again. The `pwa-install-banner` has no dismiss of its own (see Pwa Install Banner).

#### Scenario: User dismisses notification prompt

- **WHEN** the user taps the dismiss control on the notification prompt
- **THEN** the system SHALL write the dismissal to `localStorage`
- **AND** the notification prompt SHALL NOT appear on subsequent sessions

## REMOVED Requirements

### Requirement: Dismissed Prompts Do Not Reappear

**Reason**: Replaced by "Dismissed notification prompt does not reappear". The install banner's close button and session-level dismiss are removed, so "User dismisses pwa-install-banner (session-level)" and "Session dismiss is not permanent suppression" no longer describe anything.
**Migration**: None. "User dismisses notification prompt" keeps its name in the new requirement.
