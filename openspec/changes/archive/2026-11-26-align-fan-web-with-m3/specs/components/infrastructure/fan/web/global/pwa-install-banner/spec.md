## ADDED Requirements

### Requirement: The install banner is accessible

The banner SHALL be accessible to keyboard and assistive technology users.

#### Scenario: Banner element has an accessible label

- **WHEN** the banner is rendered
- **THEN** the root `<aside>` element SHALL have an `aria-label` identifying it as the install prompt

#### Scenario: Banner is hidden, not rendered, when it is not visible

- **WHEN** the banner is not visible (installed, or a post-signup surface is open)
- **THEN** the banner element SHALL carry the `hidden` and `inert` attributes, and once its exit motion has ended it SHALL NOT be rendered (`display: none`), so it is not in the accessibility tree
- **AND** its install button SHALL NOT be reachable via keyboard navigation, during the exit motion as well as after it
- **AND** the banner SHALL stay in the DOM so that its exit motion can play

### Requirement: Install banner presentation, attention cue and reduced motion

The `pwa-install-banner` SHALL use the same presentation and attention cue as `signup-prompt-banner`. A banner is persistent, so it SHALL sit on a dark surface marked by a brand-gradient line and SHALL NOT use the brand-gradient fill of the transient snack bar. It SHALL show one row, the message followed by the install button, with no icon and no close control. The install button SHALL be the filled button at the compact size of the snack bar's action. The message's text size SHALL follow the banner's width, between 12px and 16px, so that the message and the button label both fit on one line without truncation on every screen from 320px to 412px wide, in Japanese and English. While the banner is visible, a light SHALL run along its top brand line and then across the install button, once when the banner appears and then every 12 seconds, at most 5 times per route the fan opens; the banner and the button SHALL keep their position and size while it runs.

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
- **AND** the message SHALL have a text size between 12px and 16px

#### Scenario: Install button is the filled compact button

- **WHEN** the banner is rendered
- **THEN** the install button SHALL have the `primary` role's fill with its white `on-primary` label at 4.5:1 or more, at the compact size (32px tall, `label-large`, a touch target of at least 48 × 48 px), with the shared 12px corner radius

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

#### Scenario: Reduced motion — a short fade, no cue

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the attention cue SHALL NOT play
- **AND** the banner SHALL fade in over at most 100 ms, without a slide-up

#### Scenario: Banner slides in on appearance

- **WHEN** the banner becomes visible
- **AND** `prefers-reduced-motion` is not set to `reduce`
- **THEN** the banner SHALL animate in with a slide-up from below and a fade-in over 350ms (the app's medium motion duration), the same entrance as `signup-prompt-banner`


## REMOVED Requirements

### Requirement: Install banner accessibility

**Reason**: The banner now slides out when it goes, so it can no longer be removed from the DOM at once (`if.bind`); it is hidden with `hidden` and `inert` and stops being rendered when the exit ends.
**Migration**: "The install banner is accessible" holds the same two scenarios, with the second rewritten for the hidden banner.

### Requirement: Install banner presentation and attention cue

**Reason**: Under reduced motion the banner now fades in over at most 100 ms instead of appearing at once, so the requirement and its scenario "Reduced motion — no animation" no longer hold.
**Migration**: "Install banner presentation, attention cue and reduced motion" holds the same scenarios, with that one renamed "Reduced motion — a short fade, no cue".

## MODIFIED Requirements

### Requirement: Banner Suppressed While Post-Signup Dialog Is Open

The banner SHALL NOT be visible while the post-signup dialog is open to avoid visual conflict at the bottom of the screen.

#### Scenario: Post-signup dialog open — banner hidden

- **WHEN** the post-signup dialog is open
- **THEN** the system SHALL suppress the banner
- **AND** the banner SHALL be hidden and inert

#### Scenario: Post-signup dialog closed — banner visible

- **WHEN** the post-signup dialog is closed (user taps Later/Close)
- **AND** the system determines the install banner should be shown
- **THEN** the banner SHALL be rendered visible, neither hidden nor inert

### Requirement: Banner Disappears Permanently After Installation

The system SHALL stop showing the banner permanently once the app is installed.

#### Scenario: App installed via native dialog

- **WHEN** the browser fires the `appinstalled` event
- **THEN** the system SHALL determine the banner should no longer be shown
- **AND** the banner SHALL slide out and stay hidden and inert
- **AND** the banner SHALL NOT reappear in subsequent sessions

#### Scenario: App installed confirmed manually (iOS)

- **WHEN** the user confirms manual installation
- **THEN** the system SHALL determine the banner should no longer be shown
- **AND** the banner SHALL slide out and stay hidden and inert
- **AND** the banner SHALL NOT reappear in subsequent sessions
