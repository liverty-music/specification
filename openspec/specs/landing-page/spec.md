## Requirements

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

### Requirement: Guest-Friendly Welcome Copy

The Welcome page SHALL communicate that no account is required to try the product, and SHALL place this message where the primary CTA's intent is most clearly disambiguated.

#### Scenario: Guest-friendly copy displayed near primary CTA

- **WHEN** the Welcome page renders
- **THEN** the page SHALL display copy equivalent to "アカウント不要でお試しいただけます" in immediate visual proximity to the primary CTA
- **AND** the copy MAY be rendered as a caption directly below the CTA label, as a sub-line above the CTA group, or as inline microcopy adjacent to the button — whichever placement keeps the message visible without requiring the user to scroll past the CTA
- **AND** the copy SHALL NOT be hidden inside an expandable affordance or relegated below other less-relevant text

### Requirement: Authenticated User Redirect

The system SHALL redirect already-authenticated users away from the landing page to the Dashboard, regardless of `onboardingStep` value.

#### Scenario: Authenticated user visits landing page

- **WHEN** an authenticated user navigates to `/`
- **THEN** the system SHALL redirect to the Dashboard with full unrestricted access
- **AND** the system SHALL NOT check `onboardingStep`

#### Scenario: Redirect target check fails

- **WHEN** the redirect fails due to a network or API error
- **THEN** the system SHALL display the landing page with an error toast: "Could not determine account status. Please try signing in again."
- **AND** the system SHALL NOT crash to a white screen
- **AND** the system SHALL allow the user to manually navigate via the Log In button

### Requirement: Welcome Page Language Switcher

The landing page SHALL provide a language toggle for unauthenticated users to switch between supported locales without requiring sign-in.

#### Scenario: Language toggle visible on welcome page
- **WHEN** an unauthenticated user visits the welcome page
- **THEN** the system SHALL display a language toggle on Screen 1, below the hero subtitle and above the scroll-affordance button (or the inline fallback CTA group when preview data is unavailable)
- **AND** the toggle SHALL show all supported languages (EN, JA)
- **AND** the current active language SHALL be visually distinguished (e.g., bold or underline)

#### Scenario: Switching language on welcome page
- **WHEN** the user taps a language option
- **THEN** the system SHALL call `i18n.setLocale(lang)` to update all translated strings immediately
- **AND** the system SHALL persist the choice via `localStorage.setItem('language', lang)`
- **AND** no page reload SHALL be required

#### Scenario: Language preference persists across sessions
- **WHEN** the user selects a language on the welcome page and later returns
- **THEN** the i18next language detector SHALL read the persisted `language` key from localStorage
- **AND** the application SHALL start in the previously selected language
