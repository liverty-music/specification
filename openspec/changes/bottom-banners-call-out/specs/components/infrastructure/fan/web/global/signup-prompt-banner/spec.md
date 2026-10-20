## ADDED Requirements

### Requirement: Shared banner presentation and attention cue

The signup prompt banner SHALL be implemented as a shared component reusable across pages. The banner SHALL NOT offer the user any UI affordance to dismiss it; visibility is entirely controlled by the host page via the `visible` bindable. A banner is persistent, so it SHALL sit on a dark surface marked by a brand-gradient line, with the same surface, placement, layout, button, message text and attention cue as `pwa-install-banner`, and SHALL NOT use the brand-gradient fill of the transient snack bar. It SHALL show one row, the message followed by the Sign Up button. The Sign Up button SHALL be the filled button at the compact size of the snack bar's action. The message and the button label SHALL share one text size that follows the banner's width, between 12px and 16px, so that both fit on one line without truncation on every screen from 320px to 412px wide, in Japanese and English. While the banner is visible, a light SHALL run along its top brand line and then across the Sign Up button, once when the banner appears and then every 12 seconds, at most 5 times per route the fan opens; the banner and the button SHALL keep their position and size while it runs.

#### Scenario: Component renders consistently

- **WHEN** the signup-prompt-banner component is used on different pages
- **THEN** the visual style SHALL be consistent (same padding, typography, button style)
- **AND** the component SHALL accept a `message` attribute for page-specific copy
- **AND** the component SHALL be fixed-positioned with its bottom edge at the bottom navigation bar's height plus the bottom safe-area inset, so that it follows the navigation bar's height if that changes

#### Scenario: No dismiss control

- **WHEN** the signup-prompt-banner is rendered
- **THEN** the banner template SHALL NOT contain a dismiss control (no `X` button, no `Dismiss` link, no swipe-to-dismiss gesture handler)
- **AND** the banner SHALL NOT emit a `banner-dismissed` custom event under any condition
- **AND** the host page SHALL NOT need to provide a `banner-dismissed.trigger` binding or `onBannerDismissed` handler

#### Scenario: Banner has frosted glass background

- **WHEN** the signup-prompt-banner is rendered
- **THEN** the banner background SHALL be the app's base surface colour at 85% opacity with a backdrop blur, the same surface as `pwa-install-banner`
- **AND** the top border SHALL display a 2px gradient from `--color-brand-primary` to `--color-brand-secondary`
- **AND** the banner SHALL NOT be filled with the brand gradient

#### Scenario: Message and button fit one line

- **WHEN** the signup-prompt-banner is shown on a screen 320px, 360px, 375px or 412px wide, in Japanese or in English
- **THEN** the message and the Sign Up button SHALL sit side by side on one row, each on one line, with no ellipsis and no clipped text
- **AND** the message and the button label SHALL have the same text size, between 12px and 16px

#### Scenario: Sign Up button is the filled compact button

- **WHEN** the signup-prompt-banner is rendered
- **THEN** the Sign Up button SHALL have the `primary` role's fill with its white `on-primary` label at 4.5:1 or more, 36px tall, with the shared 12px corner radius and bold label

#### Scenario: Banner message text

- **WHEN** the signup-prompt-banner is rendered
- **THEN** the message SHALL use the primary text colour at full opacity and font weight 500, the same as `pwa-install-banner`'s message
- **AND** the message SHALL measure at least 4.5:1 against the banner's surface

#### Scenario: CTA attention cue

- **WHEN** the signup-prompt-banner becomes visible and stays visible on one route
- **AND** the user has not set `prefers-reduced-motion: reduce`
- **THEN** a light SHALL run along the banner's top brand line and then across the Sign Up button when the banner appears, and again every 12 seconds
- **AND** the cue SHALL play at most 5 times on that route, then the banner SHALL stay still
- **AND** the banner and the Sign Up button SHALL keep their position and size while the cue plays

#### Scenario: CTA button has no animation for reduced motion

- **WHEN** the signup-prompt-banner is rendered
- **AND** the user has set `prefers-reduced-motion: reduce`
- **THEN** the attention cue SHALL NOT play

#### Scenario: Banner slides in on appearance

- **WHEN** the signup-prompt-banner becomes visible
- **AND** the user has not set `prefers-reduced-motion: reduce`
- **THEN** the banner SHALL animate in from below with a slide-up and fade-in transition over 350ms (the app's medium motion duration), the same entrance as `pwa-install-banner`

#### Scenario: Banner appears instantly for reduced motion

- **WHEN** the signup-prompt-banner becomes visible
- **AND** the user has set `prefers-reduced-motion: reduce`
- **THEN** the banner SHALL appear immediately without animation

## MODIFIED Requirements

### Requirement: Guest Signup Prompt Banner

The system SHALL display a non-modal signup prompt banner to guest users after onboarding completion. The banner copy SHALL fit on one line next to its button on mobile and SHALL be consistent in intent across English and Japanese locales. The button SHALL read "Sign Up" in both locales.

#### Scenario: Banner copy — Japanese

- **WHEN** the signup prompt banner is displayed to a guest user in Japanese locale
- **THEN** the banner SHALL display: 「フォロー履歴を保存しよう！」
- **AND** the banner SHALL include a [Sign Up] CTA button

#### Scenario: Banner copy — English

- **WHEN** the signup prompt banner is displayed to a guest user in English locale
- **THEN** the banner SHALL display: "Save your follows!"
- **AND** the banner SHALL include a [Sign Up] CTA button

## REMOVED Requirements

### Requirement: Shared Banner Component

**Reason**: Replaced by "Shared banner presentation and attention cue", which drops the three-time glow and adds the one-row layout, the filled compact button, the fitted text and the recurring cue.
**Migration**: None. Its scenarios that still hold keep their names in the new requirement.
