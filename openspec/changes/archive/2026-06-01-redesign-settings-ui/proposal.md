## Why

The Settings page (`frontend`, Aurelia 2 PWA) has a confirmed layout defect and several UX/spec-conformance gaps. The toggle switch collapses and its thumb visibly overflows the card edge when paired with long descriptions (reproduced empirically at 412px: the declared 44px track renders at 20.63px and the thumb pokes 4px past the card border). Separately, the guest sign-in entry is buried at the bottom as a plain list row indistinguishable from legal links, and the second analytics consent toggle is mislabeled as a geographic ("overseas processing") control when it actually binds to the `marketingMeasurement` consent purpose, creating a labeling mismatch with the `analytics-consent` requirements.

## What Changes

- Fix the toggle control so its track keeps its intended size and the thumb never overflows the track or card, regardless of adjacent description length.
- Restructure each toggle row so a long description can be expanded/collapsed without compromising the switch's accessibility semantics (split the single `role="switch"` button into a disclosure control plus the switch).
- Rewrite the Privacy & Analytics consent copy to be opt-in friendly (benefit-led, with explicit "no PII / can be turned off" reassurance).
- **Relabel the marketing-measurement consent toggle to describe its purpose ("ad-effectiveness measurement") instead of geography ("overseas processing").** The toggle is NOT removed — it remains the user-controlled, persistent opt-out the `analytics-consent` requirements mandate.
- Relocate the guest sign-in / sign-up call to action from the bottom ACCOUNT section to a visually emphasized hero at the TOP of the Settings page (guest-only); authenticated account controls (email, verification, sign out) remain in the bottom ACCOUNT section.
- Show the iOS-specific sound-effects hint only on iOS (or generalize the wording) instead of on every platform.
- Remove the orphan `.settings-guest-prompt` class (applied in markup, undefined in CSS) as part of the guest-CTA rework.

## Capabilities

### New Capabilities
<!-- None — all changes are to the existing settings capability. -->

### Modified Capabilities
- `settings`: Toggle controls gain a layout-integrity requirement (track sizing and thumb containment). Toggle rows gain an expandable-description requirement with preserved switch semantics. The Privacy & Analytics consent toggles gain a labeling requirement (labels describe the consent purpose, not data geography). The existing "Guest-Adaptive Account Section" requirement is modified to relocate the guest call to action to a prominent top-of-page hero, separated from authenticated account controls. A platform-conditional requirement is added for the sound-effects hint.

## Impact

- **Frontend (Aurelia 2)**: `src/routes/settings/settings-route.{html,ts,css}` — toggle CSS (`flex-shrink`, text-column `min-inline-size`, alignment), row anatomy (disclosure + switch split), guest hero markup/styles, platform check for the sound hint, orphan-class cleanup.
- **i18n copy**: `src/locales/{ja,en}/translation.json` — `settings.analytics.*` (section/toggle copy, purpose-based marketing label), `settings.guestPrompt` / new hero strings (fixes awkward double-を phrasing), `settings.soundEffectsHint`.
- **Cross-change coordination**: The marketing-toggle relabel concerns the consent purpose introduced by the in-flight `introduce-analytics-tool` change (`analytics-consent`). This change owns only the Settings-page rendering/labeling of that purpose; the cross-border (PostHog/Netherlands) disclosure remains the responsibility of the signup consent screen and the privacy policy, not a per-region Settings toggle.
- **Tests**: `test/routes/settings-route.spec.ts`, `e2e/visual/settings.auth.visual.spec.ts` (visual baselines will need regeneration), `e2e/pwa/pwa-settings.spec.ts`.
- **No backend / proto / API changes.**
