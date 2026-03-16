## Why

The current dark theme (near-black surfaces, muted purple brand colors) feels heavy and subdued for a music platform. Users should feel the excitement of a live music festival when browsing upcoming concerts. Refreshing the visual tone to a vibrant, festival-inspired palette will make the app feel energetic and fun — especially the dashboard timetable, which should evoke the colorful stage-separated layouts seen at real music festivals like Wild Bunch Fest.

## What Changes

- **Color palette overhaul**: Replace muted purple/violet brand colors with vibrant festival palette (hot pink primary, electric blue secondary, lime green accent). Shift surface colors from near-black to deep navy with color warmth.
- **Stage identity colors**: Introduce per-stage color tokens (HOME = orange, NEAR = cyan, AWAY = magenta) so each lane is visually distinct in the dashboard timetable.
- **Typography upgrade**: Switch display font from Outfit to Righteous (festival/entertainment display face) and add Poppins as body font for a cleaner, more energetic feel.
- **Dashboard stage headers**: Color-code each stage header span with its stage color background, creating a bold festival timetable banner row.
- **Navigation vibrancy**: Add glow effects to active bottom nav tabs and gradient border accent.
- **Shadow & glow updates**: Adjust card glow and shadow tokens to reference new brand colors.
- **Text color warmth**: Shift secondary/muted text from neutral gray to slightly warm tinted values for cohesion with the new palette.

## Capabilities

### New Capabilities

_None — this change modifies existing visual tokens and styles, not new behavioral capabilities._

### Modified Capabilities

- `design-system`: Color tokens, font tokens, shadow tokens, and border tokens are all changing values. New stage color tokens are added. Typography families change from Outfit/system-ui to Righteous/Poppins.
- `typography-focused-dashboard`: Stage headers gain per-stage background colors. Lane separators use stage color accents. Date separators get gradient treatment.

## Impact

- **Frontend only** — no backend, API, or protobuf changes.
- **Files affected**:
  - `src/styles/tokens.css` — all token values updated, stage color tokens added
  - `src/styles/global.css` — body background, link colors
  - `src/styles/compositions.css` — potential new festival-themed compositions
  - `src/routes/dashboard/dashboard-route.css` — stage header colors, lane accents
  - `src/components/bottom-nav-bar/bottom-nav-bar.css` — nav glow effects
  - `src/components/page-header/page-header.css` — header gradient
  - `src/components/live-highway/event-card.css` — glow adjustments
  - `index.html` — Google Fonts link updated (Righteous + Poppins)
- **Dependencies**: Google Fonts CDN (Righteous, Poppins) — already allowed by CSP `style-src` and `font-src` directives.
- **Design system spec**: Token values change but token names remain stable — no component API breakage.
