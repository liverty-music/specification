## MODIFIED Requirements

### Requirement: Onboarding Journey Flow

The onboarding journey SHALL follow the path: Landing Page (Step 0) -> Artist Discovery (Step 1) -> Dashboard (Step 3). The Loading Sequence screen is no longer part of the onboarding flow.

> **Delta:** Previously the flow was LP -> Discover -> Loading -> Dashboard. The Loading step is removed. Users now transition directly from Discover to Dashboard when they tap the [Generate Dashboard] CTA.

#### Scenario: Discover to Dashboard transition

- **WHEN** a user is at Step 1 (Artist Discovery)
- **AND** the user has followed >= 3 artists
- **AND** the user taps the [Generate Dashboard] CTA
- **THEN** the system SHALL set `onboardingStep` to 3 (DASHBOARD)
- **AND** the system SHALL navigate to `/dashboard`
- **AND** the system SHALL NOT navigate to `/onboarding/loading`

> **Delta:** Previously, the CTA set `onboardingStep` to 2 (LOADING) and navigated to `/onboarding/loading`, which then waited 3 seconds before advancing to DASHBOARD. The intermediate step is removed.

#### Scenario: Concert data availability at Dashboard

- **WHEN** the user arrives at the Dashboard after completing Artist Discovery
- **THEN** concert data MAY already be available from the fire-and-forget `SearchNewConcerts` calls triggered during artist follows in Discovery
- **AND** the Dashboard SHALL display its own loading skeleton / promise states for any data still pending
- **AND** the system SHALL NOT rely on a loading screen to mask data fetching

> **Delta:** Previously, the loading sequence screen provided a visual bridge while concert data was assumed to be loading. Since `SearchNewConcerts` is called fire-and-forget during discovery (not during the loading screen), this bridge was cosmetic. The Dashboard's native loading states now handle any remaining data latency directly.
