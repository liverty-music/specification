## MODIFIED Requirements

### Requirement: PWA Install Prompt i18n

The PWA install banner SHALL take all user-facing text from the app's translations, so that it reads in the user's locale (Japanese or English), consistent with the notification prompt's existing i18n pattern.

#### Scenario: PWA install prompt displays localized text

- **WHEN** the PWA install banner is visible
- **THEN** the banner's accessible label, its message, its install button label and its close button's accessible name SHALL come from the translations of the user's locale
- **AND** the guide sheet's title, its steps and its "added" button label SHALL come from the same translations
- **AND** the text SHALL NOT be hardcoded in the template

### Requirement: Banner Visual Presentation

The `pwa-install-banner` SHALL use the same visual design language as `signup-prompt-banner`: the persistent-banner surface, placement, action glow and message text below. A banner is persistent, so it SHALL sit on a dark surface marked by a brand-gradient line, and SHALL NOT use the brand-gradient fill of the transient snack bar.

#### Scenario: Banner is fixed at the bottom above the nav bar

- **WHEN** the banner is visible
- **THEN** the banner SHALL be positioned fixed with its bottom edge at the bottom navigation bar's height plus the bottom safe-area inset, so that it follows the navigation bar's height if that changes
- **AND** the banner SHALL span the full inline width of the screen (`inset-inline: 0`)

#### Scenario: Banner frosted glass and gradient border

- **WHEN** the banner is rendered
- **THEN** the background SHALL be the app's base surface colour at 85% opacity with a backdrop blur, the same surface as `signup-prompt-banner`
- **AND** the top border SHALL be a 2px gradient from `--color-brand-primary` to `--color-brand-secondary`
- **AND** the banner SHALL NOT be filled with the brand gradient

#### Scenario: CTA button glow pulse animation

- **WHEN** the banner becomes visible
- **AND** `prefers-reduced-motion` is not set to `reduce`
- **THEN** the CTA button SHALL glow in `--color-brand-primary` three times, over 1.2 seconds each, the timing of the snack bar's attention glow
- **AND** the CTA button SHALL then stay still for as long as the banner is shown

#### Scenario: Banner message text

- **WHEN** the banner is rendered
- **THEN** the message SHALL use the primary text colour at full opacity and font weight 500, the same as `signup-prompt-banner`'s message
- **AND** the message SHALL measure at least 4.5:1 against the banner's surface

#### Scenario: Reduced motion — no animation

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the CTA button glow animation SHALL be suppressed
- **AND** the banner SHALL appear without a slide-up animation

#### Scenario: Banner slides in on appearance

- **WHEN** the banner becomes visible
- **AND** `prefers-reduced-motion` is not set to `reduce`
- **THEN** the banner SHALL animate in with a slide-up from below and a fade-in over 350ms (the app's medium motion duration), the same entrance as `signup-prompt-banner`

## REMOVED Requirements

### Requirement: Prompt Entrance and Exit Animations

**Reason**: It describes an earlier install prompt: a 600ms fade-slide-up on entry and a fade-slide-down on exit, during which the element stays in the DOM. The install banner instead slides in as stated in "Banner Visual Presentation", and it is removed from the DOM at once when hidden ("Banner is removed from DOM when hidden" under "Banner Accessibility"). The notification prompt has no entrance or exit animation. The requirement contradicts both and no code meets it.
**Migration**: None. The install banner's entrance and its reduced-motion behaviour are stated in "Banner Visual Presentation".
