## Context

Small bugfix — no design artifact needed. Both fixes are straightforward data-flow corrections in existing components.

## Decisions

1. **Home area i18n key**: Store the romaji i18n key (via `translationKey()`) instead of the Japanese display name (via `shortDisplayName()`). This aligns `currentHome` with the i18n translation file keys.

2. **Language selector UI**: Use a bottom sheet dialog (same pattern as `UserHomeSelector`) rather than the immediate `cycleLanguage()` toggle. Consistent UX across settings page interactions.
