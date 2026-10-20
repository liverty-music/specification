# Signup Prompt Banner

## Purpose

Provide a persistent fixed banner on My Artists and Dashboard pages prompting unauthenticated users to create an account, dismissed automatically on signup completion.

## Requirements

### Requirement: Guest Signup Prompt Banner

The system SHALL display a non-modal signup prompt banner to guest users after onboarding completion. The banner copy SHALL be concise (≤2 lines on mobile) and SHALL be consistent in intent across English and Japanese locales.

#### Scenario: Banner copy — Japanese

- **WHEN** the signup prompt banner is displayed to a guest user in Japanese locale
- **THEN** the banner SHALL display: "フォロー情報を保存してコンサート通知を受け取ろう！"
- **AND** the banner SHALL include a [アカウント作成] CTA button

#### Scenario: Banner copy — English

- **WHEN** the signup prompt banner is displayed to a guest user in English locale
- **THEN** the banner SHALL display: "Save your followed artists and get concert notifications."
- **AND** the banner SHALL include a [Create Account] CTA button

### Requirement: Shared Banner Component

The signup prompt banner SHALL be implemented as a shared component reusable across pages. The banner SHALL NOT offer the user any UI affordance to dismiss it; visibility is entirely controlled by the host page via the `visible` bindable. A banner is persistent, so it SHALL sit on a dark surface marked by a brand-gradient line, the same surface, placement, action glow and message text as `pwa-install-banner`, and SHALL NOT use the brand-gradient fill of the transient snack bar.

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

#### Scenario: CTA button has glow pulse animation

- **WHEN** the signup-prompt-banner becomes visible
- **AND** the user has not set `prefers-reduced-motion: reduce`
- **THEN** the "Create Account" button SHALL glow in `--color-brand-primary` three times, over 1.2 seconds each with ease-in-out timing, the timing of the snack bar's attention glow
- **AND** the button SHALL then stay still for as long as the banner is shown

#### Scenario: CTA button has no animation for reduced motion

- **WHEN** the signup-prompt-banner is rendered
- **AND** the user has set `prefers-reduced-motion: reduce`
- **THEN** the "Create Account" button SHALL NOT display the glow animation

#### Scenario: Banner message text

- **WHEN** the signup-prompt-banner is rendered
- **THEN** the message SHALL use the primary text colour at full opacity and font weight 500, the same as `pwa-install-banner`'s message
- **AND** the message SHALL measure at least 4.5:1 against the banner's surface

#### Scenario: Banner slides in on appearance

- **WHEN** the signup-prompt-banner becomes visible
- **AND** the user has not set `prefers-reduced-motion: reduce`
- **THEN** the banner SHALL animate in from below with a slide-up and fade-in transition over 350ms (the app's medium motion duration), the same entrance as `pwa-install-banner`

#### Scenario: Banner appears instantly for reduced motion

- **WHEN** the signup-prompt-banner becomes visible
- **AND** the user has set `prefers-reduced-motion: reduce`
- **THEN** the banner SHALL appear immediately without animation
