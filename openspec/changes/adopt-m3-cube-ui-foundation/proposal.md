## Why

Layouts in the fan app keep breaking because a component's stylesheet can undo the shared rules, and nothing stops it. In the All Nearby filter sheet, the list's `margin: 0` cancelled the `.flow` spacing between the title and the rows: the `block` layer comes after `composition`, and the declaration only repeated what `reset.css` already applies. Lint passed, and the story only checked that the rows were visible.

The same cause shows up across both apps:

| Measured in component stylesheets | Fan app | Organizer console |
|---|---|---|
| Margin declarations | 118 | 45 |
| Declarations that repeat `reset.css` (`margin: 0`, `padding: 0`, `list-style: none`) | 56 | 52 |
| `font-family` declarations | 53 | 2 |
| Distinct font combinations | 45 | 13 |
| `box-shadow` values with no token | 13 | 2 |
| Stylesheets over CUBE CSS's 100-line limit for a block | 32 of 67 | 8 of 40 |

The fan app also has no type roles. Colour, shape and motion follow Material 3 roles, but text picks a size from a fluid scale, so each screen sets its own heading style. The global `h1` and `h2` sizes never render. Fan controls are 44 px tall where Material 3 and the organizer console ask for 48 px, and keyboard focus has no shared style: 13 stylesheets draw their own outline.

Stylelint 18, released on 2026-11-03, has core rules that can enforce most of this without custom code. The current plugin `stylelint-use-logical` does not support it.

## What Changes

**Lint enforces the CUBE CSS layers**

- Upgrade to stylelint 18. Replace `stylelint-use-logical` and the plugin's colour-token rule with core rules, and keep a `cube/*` rule only where core has no equivalent.
- In component stylesheets, forbid margins, values that repeat `reset.css`, and font and focus-outline declarations. Accept only design tokens for colour, radius, spacing and shadow.
- Lower the block limit from 510 to 100 lines. A block over the limit becomes smaller components.
- Require every lint-disable comment to state a reason, and report unused ones.
- Enable all of this in the first commit, with existing violations recorded by stylelint's bulk suppressions. The recorded list is the work list; **the change is complete when it is empty**.

**Both apps adopt Material 3 Expressive foundations**

- **BREAKING for stylesheets:** tokens move to the official `--md-sys-*` names. `--step-*`, `--leading-*`, `--font-*`, `--radius-*`, `--shadow-*`, `--transition-*`, `--container-*` and the role-like `--color-*` tokens are removed. Brand, stage and status colours have no Material 3 role and keep their `--color-*` names. Spacing has no Material 3 token and stays `--space-*`.
- Add the 15 baseline and 15 emphasized type styles at fixed `rem` sizes; the fluid type scale goes away. Text gets its style from a utility class (`md-typescale-title-large`).
- Fix `--space-*` at 4, 8, 12, 16, 24, 32 and 48 px in both apps, plus the fan app's 64 and 96 px.
- Add elevation levels, one global focus ring (3 px, offset 2 px), a 48 px minimum touch target, the Material 3 breakpoints and a higher-contrast colour set under `prefers-contrast: more`.
- Share the type scale, elevation, focus ring size, touch target and breakpoints through `shared/styles/`, as state and motion already are. Colour, shape and the brand typeface stay per app.

**Typefaces**

- The variable Noto Sans JP becomes the text typeface in both apps, so Japanese text looks the same on every device. Poppins and Outfit are removed from the fan app, and the organizer console stops relying on system fonts.
- The fan app uses Righteous for display and headline styles. The organizer console is a calm work tool and has no brand typeface: every style there uses Noto Sans JP.

**Fan app shared components and sizes**

- `<bottom-sheet>` gets a heading, replacing each sheet's own title style.
- One `<list-item>` replaces the settings rows and the All Nearby filter rows.
- The navigation bar becomes 64 px tall, sheets get a 28 px corner, and icons use four named sizes with 24 px as the standard.

## Capabilities

### New Capabilities

None. CSS architecture rules stay in `stylelint.config.js` and its tests, which are the contract; `AGENTS.md` points to them. A spec would only restate them without enforcing anything.

### Modified Capabilities

- `components/infrastructure/fan/web/global/design-tokens`: type scale, typefaces, fixed spacing, elevation, focus ring, touch target, breakpoints, higher-contrast colours; what is shared with the organizer console.
- `components/infrastructure/organizer/web/global/design-tokens`: the same shared tokens; its type scale gains the remaining styles in `rem`, and its typeface becomes Noto Sans JP.
- `components/infrastructure/fan/web/global/ui-primitives`: named icon sizes and the shared list item.
- `components/infrastructure/fan/web/global/bottom-sheet`: the sheet heading and Material 3 container values; token names replaced by roles.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: 64 px height.
- `components/infrastructure/fan/web/global/page-header`, `page-help`, `toast`, `live-highway`: scenarios that name removed tokens now name roles and type styles.
- `components/infrastructure/fan/web/route/my-artists`, `route/welcome`, `route/dashboard`, `global/app-shell`: tap targets rise from 44 px to 48 px.

## Impact

- **frontend only:** `stylelint.config.js`, `stylelint-plugin-cube-css/`, `src/styles/`, `shared/styles/`, `organizer/styles/`, `index.html` and `organizer.html` (fonts), `organizer/guide/guide.html`, and nearly every component stylesheet and many templates in the fan app and the organizer console. Admin and reception are out of scope, but they run under the upgraded stylelint.
- **Dependencies:** `stylelint` 17 → 18 and `stylelint-config-standard` 40 → 41; `stylelint-use-logical` removed.
- **Visible change on every fan screen:** text sizes, spacing, touch targets, navigation bar height. Visual baselines are regenerated as screens move. The organizer console changes little: its type and spacing values already match.
- **Loading:** Noto Sans JP is large, though Google Fonts serves it in subsets by Unicode range. The cost is measured against production before release.
- **No API, proto, backend or infrastructure change.** `font-src` already allows `fonts.gstatic.com`.
- **Concurrent work:** other changes that edit stylesheets conflict with the renames; the renames land as one mechanical commit per token family to keep conflicts small.
- **Delivery:** more than one frontend PR, a deliberate exception to "one PR per repository". See design.md.
