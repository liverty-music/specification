## MODIFIED Requirements

### Requirement: Hero Screen Scroll Affordance

The landing page Screen 1 SHALL provide a single, clearly labeled affordance that invites the user to reveal the guided demo below, whenever the demo is rendered. This affordance SHALL be the only primary interactive control on Screen 1 (apart from the language switcher) when the demo is present, preserving the "message-first" intent of the hero screen. When the demo is not rendered (no preview data), the scroll-affordance SHALL NOT be displayed, because there is no target to scroll to — the inline CTA fallback takes its place (see `Passkey Authentication CTA`). The affordance label and behavior are unchanged from the prior single-preview-screen design.

#### Scenario: Scroll affordance button is rendered when preview is available

- **WHEN** an unauthenticated user visits `/` and views Screen 1, and preview data is available
- **THEN** the system SHALL display a labeled scroll-affordance button within Screen 1
- **AND** the button SHALL be rendered as a `<button>` element
- **AND** the button SHALL have a minimum tap target of 48×48px
- **AND** the button SHALL be focusable via keyboard navigation
- **AND** the visible focus indicator SHALL be preserved under keyboard focus

#### Scenario: Tapping the scroll affordance reveals the preview

- **WHEN** the user taps or activates the scroll-affordance button
- **THEN** the system SHALL scroll the viewport to the guided demo below the hero
- **AND** the scrolling SHALL use smooth-scroll animation by default

#### Scenario: Reduced motion preference disables smooth scroll

- **WHEN** the user has `prefers-reduced-motion: reduce` set in their environment
- **AND** the user activates the scroll-affordance button
- **THEN** the system SHALL jump directly to the demo without a smooth-scroll animation

#### Scenario: Scroll affordance hidden when preview data is unavailable

- **WHEN** an unauthenticated user visits `/` and preview data is unavailable
- **THEN** the system SHALL NOT render the scroll-affordance button
- **AND** the hero Screen 1 SHALL instead render inline `[Get Started]` and `[Log In]` CTAs (see `Passkey Authentication CTA`)

#### Scenario: Button label is localized

- **WHEN** the landing page is rendered in Japanese
- **THEN** the button label SHALL display the Japanese scroll-affordance label
- **WHEN** the landing page is rendered in English
- **THEN** the button label SHALL display the English scroll-affordance label

### Requirement: Sign-in help link next to Log In

Wherever the welcome page shows the `[Log In]` CTA, it SHALL show a "can't sign in" text link directly below it that opens the passkey recovery screen. The link SHALL be a native link with a minimum tap target of 48px height.

#### Scenario: Link below Log In

- **WHEN** an unauthenticated user sees the `[Log In]` CTA on Screen 2 or in the Screen 1 fallback
- **THEN** a "can't sign in" link is shown directly below it

#### Scenario: Link opens the recovery screen

- **WHEN** the user taps the "can't sign in" link
- **THEN** the app navigates to `/passkey-recovery`
