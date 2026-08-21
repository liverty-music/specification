## REMOVED Requirements

### Requirement: FAB Visible After Onboarding Completion

**Reason**: Replaced by `pwa-install-banner`, which provides greater visual prominence and includes iOS in a unified banner component.
**Migration**: Users are shown `pwa-install-banner` instead. See `pwa-install-banner` capability spec.

### Requirement: FAB Install Behavior by Platform

**Reason**: Install flow by platform is now handled by `pwa-install-banner` (native CTA mode and guide sheet mode).
**Migration**: See `pwa-install-banner` — Requirement: Banner CTA Install Flow by Platform.

### Requirement: FAB Disappears After Installation

**Reason**: Permanent removal after installation is now handled by `pwa-install-banner`.
**Migration**: See `pwa-install-banner` — Requirement: Banner Disappears Permanently After Installation.

### Requirement: FAB Entry Animation

**Reason**: Animation is replaced by the `pwa-install-banner` slide-up and pulsing CTA button.
**Migration**: See `pwa-install-banner` — Requirement: Banner Visual Presentation.

### Requirement: FAB Icon Size

**Reason**: FAB component is deleted; no equivalent in the banner component.
**Migration**: Not applicable.

### Requirement: FAB Accessibility State

**Reason**: Accessibility is now handled by `pwa-install-banner`.
**Migration**: See `pwa-install-banner` — Requirement: Banner Accessibility.

### Requirement: FAB Position When signup-prompt-banner Is Visible

**Reason**: The FAB coexistence layout with `signup-prompt-banner` is no longer needed. `pwa-install-banner` is shown only to authenticated users; `signup-prompt-banner` is shown only to guests — the two banners are mutually exclusive by user state.
**Migration**: Not applicable.
