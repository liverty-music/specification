## Context

The Liverty Music frontend uses a CUBE CSS architecture with design tokens centralized in `tokens.css`. The current palette is a dark-first theme with muted purple brand colors and near-black surfaces (`oklch(14.5%)`). The dashboard uses a 3-lane subgrid layout for HOME/NEAR/AWAY stages but all lanes share the same monochrome visual treatment.

The existing token system is well-structured — all components reference `--color-*`, `--font-*`, `--shadow-*` tokens rather than hardcoded values. This means a palette swap at the token level propagates automatically to all components. Component-level CSS changes are only needed where new tokens (stage colors) are introduced or where new visual effects (gradients, glows) are added.

## Goals / Non-Goals

**Goals:**
- Transform the visual tone from "dark and subdued" to "vibrant festival" by updating design token values
- Give each dashboard stage (HOME/NEAR/AWAY) a distinct color identity
- Upgrade typography to festival-appropriate display + body fonts
- Consolidate tone-and-manner into `tokens.css` — all color, font, and shadow definitions live in `:root` custom properties; components reference tokens only
- Maintain WCAG AA contrast ratios with the new palette
- Follow CUBE CSS layer discipline: compositions stay layout-only; visual treatment (stage colors, glows) lives in block/exception layers

**Non-Goals:**
- No layout/structure changes — the 3-lane subgrid, app-shell grid, and component hierarchy remain unchanged
- No new components or routes
- No backend, API, or data model changes
- No light theme — this remains dark-first (but warmer/more colorful dark)
- No animation overhaul — existing keyframes and transitions stay
- No new composition primitives — existing compositions (`flow`, `cluster`, `stack`, `wrapper`, `grid-auto`, `center`) are sufficient

## Decisions

### 1. Token-level palette swap (not component-level overrides)

**Decision**: Change token values in `tokens.css` `:root` rather than adding component-scoped color overrides.

**Rationale**: The existing token architecture already ensures all components reference central tokens. Changing values at the source gives us site-wide consistency with minimal file changes. Components only need modification where new tokens (stage colors) are consumed.

**Alternative considered**: CSS custom property overrides per-component or per-route. Rejected because it fragments the design system and creates maintenance burden.

### 2. OKLCH color space preserved with relative color syntax for derived values

**Decision**: Keep all color definitions in OKLCH. Use relative color syntax (`oklch(from var(--token) l c h / N%)`) for derived values like shadows and opacity variants.

**Rationale**: OKLCH is already used throughout. Relative color syntax ensures derived values (shadow glows, border accents) stay in sync when the source token changes — no hardcoded oklch literals scattered across files. This aligns with the CUBE CSS principle of tokens as single source of truth.

### 3. Font loading strategy: additive, not replacement

**Decision**: Add Righteous and Poppins via new Google Fonts `<link>` tags. Retain the existing Outfit `<link>` as it serves as the second fallback in the `--font-display` stack.

**Rationale**: Google Fonts is already in the CSP allowlist. Using `display=swap` prevents invisible text during load. Keeping Outfit loaded means graceful degradation if Google Fonts CDN is slow for the new fonts. The font stack `"Righteous", "Outfit", system-ui` ensures progressive enhancement.

**Alternative considered**: Self-hosting fonts via `@font-face` in the bundle. Rejected for now — adds build complexity; Google Fonts CDN with preconnect is sufficient for current scale.

### 4. Stage colors as first-class tokens, applied via block/exception pattern

**Decision**: Add `--color-stage-home`, `--color-stage-near`, `--color-stage-away` to `:root` in `tokens.css`. Apply them in component block layers via `data-stage` attribute selectors (CUBE CSS exception pattern).

**Rationale**: Stage identity is a core domain concept. Making them first-class tokens means any component can reference them. The visual application (background color, text color) belongs in each component's block `@scope`, not in a composition — CUBE CSS compositions must remain layout-only (no color, font-style, shadows, backgrounds).

**Alternative considered**: Creating a `.stage-banner` composition class. Rejected because compositions must not contain visual treatment per CUBE CSS methodology. The `data-stage` attribute is already present in the HTML template, making it a natural exception selector.

### 5. Righteous font-weight: 400 only

**Decision**: All uses of `--font-display` SHALL use `font-weight: normal` (400) or omit weight entirely.

**Rationale**: Righteous ships only weight 400. Specifying `font-weight: 700` (currently used in stage headers, page headers, and event card titles) causes browsers to synthesize faux-bold, which looks poor with display typefaces. Righteous is inherently bold-looking at its native weight.

### 6. Bottom nav glow via box-shadow + pseudo-element gradient border

**Decision**: Use `box-shadow` for active tab glow. Use a `::before` pseudo-element with `background-image: linear-gradient(...)` for the gradient top border.

**Rationale**: `box-shadow` is GPU-composited, doesn't affect layout, and works with existing `transition: color`. The gradient border uses `::before` instead of `border-image` because `border-image` disables `border-radius` per CSS spec — even though the current nav has no radius, this prevents future breakage.

## Risks / Trade-offs

**[Risk] Contrast regression with new palette** → All new color combinations will be verified against WCAG AA (4.5:1 for body text, 3:1 for large text). The deep navy surface (`oklch(18%)`) is still dark enough to provide strong contrast with near-white text. Stage banner text uses `--color-surface-base` (dark) on vibrant backgrounds — requires verification.

**[Risk] Google Fonts dependency for three fonts** → If Google Fonts CDN is unavailable: Righteous falls back to Outfit (still loaded), Poppins falls back to system-ui. No broken layout, just reduced visual flair.

**[Risk] Stage colors too saturated for card backgrounds** → Stage color tokens use moderate chroma (0.18–0.25) at medium lightness (68–75%). For card backgrounds, components will use `oklch(from var(--color-stage-*) l c h / N%)` relative color syntax to reduce opacity. Full-chroma values are intended for stage header backgrounds only.

**[Trade-off] Righteous is a single-weight font** → This limits heading weight variation. Accepted because the font's inherent boldness and distinctive character compensate. Existing `font-weight: 700` declarations must be updated to `normal` to prevent faux-bold.

**[Risk] Relative color syntax in shadow tokens** → `oklch(from var(...) l c h / N%)` is Baseline Newly Available (2024). All target browsers support it. No fallback needed for the current user base.
