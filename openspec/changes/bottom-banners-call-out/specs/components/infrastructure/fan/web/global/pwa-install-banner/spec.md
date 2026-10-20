## ADDED Requirements

### Requirement: Install banner presentation and attention cue

The `pwa-install-banner` SHALL use the same presentation and attention cue as `signup-prompt-banner`. A banner is persistent, so it SHALL sit on a dark surface marked by a brand-gradient line and SHALL NOT use the brand-gradient fill of the transient snack bar. It SHALL show one row, the message followed by the install button, with no icon and no close control. The install button SHALL be the filled button at the compact size of the snack bar's action. The message and the button label SHALL share one text size that follows the banner's width, between 12px and 16px, so that both fit on one line without truncation on every screen from 320px to 412px wide, in Japanese and English. While the banner is visible, a light SHALL run along its top brand line and then across the install button, once when the banner appears and then every 12 seconds, at most 5 times per route the fan opens; the banner and the button SHALL keep their position and size while it runs.

#### Scenario: Banner is fixed at the bottom above the nav bar

- **WHEN** the banner is visible
- **THEN** the banner SHALL be positioned fixed with its bottom edge at the bottom navigation bar's height plus the bottom safe-area inset, so that it follows the navigation bar's height if that changes
- **AND** the banner SHALL span the full inline width of the screen (`inset-inline: 0`)

#### Scenario: Banner frosted glass and gradient border

- **WHEN** the banner is rendered
- **THEN** the background SHALL be the app's base surface colour at 85% opacity with a backdrop blur, the same surface as `signup-prompt-banner`
- **AND** the top border SHALL be a 2px gradient from `--color-brand-primary` to `--color-brand-secondary`
- **AND** the banner SHALL NOT be filled with the brand gradient

#### Scenario: One row with no icon or close control

- **WHEN** the banner is rendered
- **THEN** it SHALL show the message and the install button side by side on one row
- **AND** it SHALL show no app icon and no close control

#### Scenario: Message and button fit one line

- **WHEN** the banner is shown on a screen 320px, 360px, 375px or 412px wide, in Japanese or in English
- **THEN** the message and the install button label SHALL each fit on one line, with no ellipsis and no clipped text
- **AND** the message and the button label SHALL have the same text size, between 12px and 16px

#### Scenario: Install button is the filled compact button

- **WHEN** the banner is rendered
- **THEN** the install button SHALL have a fill in brand-primary's hue, dark enough that its white label measures at least 4.5:1, 36px tall, with the shared 12px corner radius and bold label

#### Scenario: Banner message text

- **WHEN** the banner is rendered
- **THEN** the message SHALL use the primary text colour at full opacity and font weight 500, the same as `signup-prompt-banner`'s message
- **AND** the message SHALL measure at least 4.5:1 against the banner's surface

#### Scenario: CTA attention cue

- **WHEN** the banner becomes visible and stays visible on one route
- **AND** `prefers-reduced-motion` is not set to `reduce`
- **THEN** a light SHALL run along the banner's top brand line and then across the install button when the banner appears, and again every 12 seconds
- **AND** the cue SHALL play at most 5 times on that route, then the banner SHALL stay still
- **AND** opening another route SHALL let the cue play again, at most 5 times there
- **AND** the banner and the install button SHALL keep their position and size while the cue plays

#### Scenario: Reduced motion — no animation

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the attention cue SHALL NOT play
- **AND** the banner SHALL appear without a slide-up animation

#### Scenario: Banner slides in on appearance

- **WHEN** the banner becomes visible
- **AND** `prefers-reduced-motion` is not set to `reduce`
- **THEN** the banner SHALL animate in with a slide-up from below and a fade-in over 350ms (the app's medium motion duration), the same entrance as `signup-prompt-banner`

### Requirement: Install banner accessibility

The banner SHALL be accessible to keyboard and assistive technology users.

#### Scenario: Banner element has an accessible label

- **WHEN** the banner is rendered
- **THEN** the root `<aside>` element SHALL have an `aria-label` identifying it as the install prompt

#### Scenario: Banner is removed from DOM when hidden

- **WHEN** the banner is not visible (installed, or a post-signup surface is open)
- **THEN** the banner element SHALL be removed from the DOM (`if.bind`, not `show.bind`)
- **AND** its install button SHALL NOT be reachable via keyboard navigation

## MODIFIED Requirements

### Requirement: PWA Install Prompt i18n

The PWA install banner SHALL take all user-facing text from the app's translations, so that it reads in the user's locale (Japanese or English), consistent with the notification prompt's existing i18n pattern. The message SHALL read 「新着ライブ通知を受け取ろう！」 in Japanese and "Get new show alerts!" in English, and the install button SHALL read "Install" in both.

#### Scenario: PWA install prompt displays localized text

- **WHEN** the PWA install banner is visible
- **THEN** the banner's accessible label, its message and its install button label SHALL come from the translations of the user's locale
- **AND** the guide sheet's title, its steps and its "added" button label SHALL come from the same translations
- **AND** the text SHALL NOT be hardcoded in the template

### Requirement: Banner Visible to Authenticated Non-Installed Users After Onboarding

The system SHALL display the `pwa-install-banner` to authenticated users who have not installed the PWA, once onboarding is completed. The banner SHALL NOT be shown to unauthenticated (guest) users. The banner offers no way to close it: it stays until the app is installed or the user confirms the install in the guide sheet.

#### Scenario: Authenticated user has not installed the PWA

- **WHEN** the user is authenticated
- **AND** onboarding is completed (`OnboardingStep.COMPLETED`)
- **AND** the app has not been installed
- **THEN** the system SHALL display the `pwa-install-banner`

#### Scenario: Guest user is not shown the banner

- **WHEN** the user is NOT authenticated
- **THEN** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: App already installed — banner not shown

- **WHEN** the app has been installed (detected via `localStorage['pwa.installed']`, `navigator.standalone === true`, or `display-mode: standalone`)
- **THEN** the system SHALL determine the banner should not be shown
- **AND** the system SHALL NOT display the `pwa-install-banner`

#### Scenario: Banner not shown during onboarding

- **WHEN** the user is in active onboarding steps (DISCOVERY, DASHBOARD, MY_ARTISTS)
- **THEN** the system SHALL NOT display the `pwa-install-banner`

### Requirement: Banner Suppressed While Post-Signup Dialog Is Open

The banner SHALL NOT be visible while the post-signup dialog is open to avoid visual conflict at the bottom of the screen.

#### Scenario: Post-signup dialog open — banner hidden

- **WHEN** the post-signup dialog is open
- **THEN** the system SHALL suppress the banner
- **AND** the banner SHALL NOT be rendered in the DOM

#### Scenario: Post-signup dialog closed — banner visible

- **WHEN** the post-signup dialog is closed (user taps Later/Close)
- **AND** the system determines the install banner should be shown
- **THEN** the banner SHALL be rendered

## REMOVED Requirements

### Requirement: Session-Level Dismiss

**Reason**: The banner has no close control any more; signing in to install the app is a strong recommendation, so the banner stays until the app is installed or the install is confirmed. The per-tab flag also behaved differently from its spec (it survived reloads while "Banner reappears on next session" said a page load clears it).
**Migration**: None. The `pwaBanner.dismissed` session key stops being read or written; a value left in a tab's session storage has no effect.

### Requirement: Banner Visual Presentation

**Reason**: Replaced by "Install banner presentation and attention cue", which drops the three-time glow and adds the one-row layout, the filled compact button, the fitted text, and the recurring cue.
**Migration**: None. Its scenarios that still hold keep their names in the new requirement.

### Requirement: Banner Accessibility

**Reason**: Replaced by "Install banner accessibility": the close button and its accessible name are gone.
**Migration**: None. Its remaining scenarios keep their names in the new requirement.
