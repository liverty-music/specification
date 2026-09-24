## ADDED Requirements

### Requirement: Post-onboarding antisocial discovery triggers deactivation

If a 反社 relationship is discovered **after** onboarding, an operator holding
the platform `admin` role SHALL **deactivate** the Organizer (reusing the
existing deactivation hook), and the breach of the 暴排条項 SHALL be a
documented ground for termination.

#### Scenario: Later discovery deactivates the organizer

- **WHEN** a 反社 relationship is discovered for an already-onboarded Organizer
- **THEN** an admin SHALL deactivate the Organizer
- **AND** the deactivation SHALL reject the Organizer's subsequent operations
  (per the existing deactivation behavior)
