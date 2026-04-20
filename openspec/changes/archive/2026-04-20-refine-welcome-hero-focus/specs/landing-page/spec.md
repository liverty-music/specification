## MODIFIED Requirements

### Requirement: Passkey Authentication CTA

The system SHALL provide both a primary `[Get Started]` CTA and a secondary `[Log In]` CTA to unauthenticated users on the landing page. When the dashboard preview is available (Screen 2 is rendered), both CTAs SHALL be rendered only within Screen 2 adjacent to the preview, and SHALL NOT appear on the hero screen (Screen 1). When the dashboard preview is unavailable and Screen 2 is not rendered, both CTAs SHALL fall back to inline placement within Screen 1 so that unauthenticated users always have a way to start onboarding or sign in. Both CTAs SHALL always be reachable on the page regardless of `onboardingStep` value. Both CTAs SHALL be rendered as `<button>` elements for accessibility.

#### Scenario: With preview data — both CTAs appear on Screen 2 only

- **WHEN** an unauthenticated user visits `/` and the preview data is available
- **THEN** the system SHALL display a primary `[Get Started]` button on Screen 2
- **AND** the system SHALL display a secondary `[Log In]` button on Screen 2, below the primary CTA
- **AND** the primary CTA SHALL use the brand accent color with a filled background
- **AND** the secondary CTA SHALL use an outline/ghost style with brand color text
- **AND** both buttons SHALL have a minimum tap target of 48px height
- **AND** neither `[Get Started]` nor `[Log In]` SHALL be rendered on Screen 1

#### Scenario: Without preview data — CTAs fall back to Screen 1

- **WHEN** an unauthenticated user visits `/` and preview data is unavailable (no Screen 2)
- **THEN** the system SHALL display the `[Get Started]` and `[Log In]` buttons inline on Screen 1 below the hero copy
- **AND** the system SHALL NOT render the `[See how it works ↓]` scroll-affordance button (since there is no Screen 2 to scroll to)
- **AND** the hero SHALL occupy the full viewport (`block-size: 100svh`) rather than the 95svh peek configuration used when Screen 2 follows

#### Scenario: Get Started initiates onboarding without clearing guest data

- **WHEN** an unauthenticated user taps `[Get Started]` (on Screen 2 or the Screen 1 fallback)
- **THEN** the system SHALL reset the onboarding step to DISCOVERY
- **AND** the system SHALL navigate to `/discovery`
- **AND** the system SHALL NOT clear previously stored guest artist data (`guest.follows`)

#### Scenario: Log In initiates OAuth sign-in

- **WHEN** an unauthenticated user taps `[Log In]` (on Screen 2 or the Screen 1 fallback)
- **THEN** the system SHALL initiate the Zitadel OIDC sign-in flow

#### Scenario: No alternative auth methods displayed

- **WHEN** the landing page is displayed
- **THEN** the system SHALL NOT display email/password fields or social login buttons (Google, Spotify, etc.)
- **AND** Passkey SHALL be the sole authentication method

## ADDED Requirements

### Requirement: Hero Screen Scroll Affordance

The landing page Screen 1 SHALL provide a single, clearly labeled affordance that invites the user to reveal the dashboard preview on Screen 2, whenever Screen 2 is rendered. This affordance SHALL be the only primary interactive control on Screen 1 (apart from the language switcher) when Screen 2 is present, preserving the "message-first" intent of the hero screen. When Screen 2 is not rendered (no preview data), the scroll-affordance SHALL NOT be displayed, because there is no target to scroll to — the inline CTA fallback takes its place (see `Passkey Authentication CTA`).

#### Scenario: Scroll affordance button is rendered when preview is available

- **WHEN** an unauthenticated user visits `/` and views Screen 1, and preview data is available
- **THEN** the system SHALL display a labeled `[See how it works ↓]` button within Screen 1
- **AND** the button SHALL be rendered as a `<button>` element
- **AND** the button SHALL have a minimum tap target of 44×44px
- **AND** the button SHALL be focusable via keyboard navigation
- **AND** the visible focus indicator SHALL be preserved under keyboard focus

#### Scenario: Tapping the scroll affordance reveals the preview

- **WHEN** the user taps or activates the `[See how it works ↓]` button
- **THEN** the system SHALL scroll the viewport to Screen 2 (the preview screen)
- **AND** the scrolling SHALL use smooth-scroll animation by default

#### Scenario: Reduced motion preference disables smooth scroll

- **WHEN** the user has `prefers-reduced-motion: reduce` set in their environment
- **AND** the user activates the `[See how it works ↓]` button
- **THEN** the system SHALL jump directly to Screen 2 without a smooth-scroll animation

#### Scenario: Scroll affordance hidden when preview data is unavailable

- **WHEN** an unauthenticated user visits `/` and preview data is unavailable
- **THEN** the system SHALL NOT render the `[See how it works ↓]` button
- **AND** the hero Screen 1 SHALL instead render inline `[Get Started]` and `[Log In]` CTAs (see `Passkey Authentication CTA`)

#### Scenario: Button label is localized

- **WHEN** the landing page is rendered in Japanese
- **THEN** the button label SHALL display a Japanese equivalent of "See how it works ↓"
- **WHEN** the landing page is rendered in English
- **THEN** the button label SHALL display "See how it works ↓" (or its configured English text)
