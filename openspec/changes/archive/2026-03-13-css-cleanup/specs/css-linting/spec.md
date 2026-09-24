## REMOVED Requirements

### Requirement: Stylelint compatible with Tailwind CSS v4
**Reason**: TailwindCSS was removed from the project in `improve-css-design`. The CUBE CSS architecture uses plain `@layer`, `@scope`, and CSS custom properties — no Tailwind directives exist in the codebase.
**Migration**: Remove `@theme` from `ignoreAtRules` and `theme()` from `ignoreFunctions` in `stylelint.config.js`. No CSS file changes needed as no Tailwind directives remain.
