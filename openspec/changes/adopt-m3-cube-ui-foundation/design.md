## Context

See proposal.md for the motivation. These facts about the frontend repository shape the approach:

- **Layers:** `src/styles/main.css` declares `reset, tokens, global, composition, utility, block, exception`. A later layer always wins, so a `block` declaration beats `.flow`.
- **File layout:** every component stylesheet in `src/`, `shared/ui/` and `organizer/` declares `@layer block`. The other layers live in `*/styles/`. The one block there is `src/styles/button.css`. Lint rules can therefore be scoped by file path rather than by layer.
- **Two ways of scoping styles:** fan components use `@scope`. Organizer components render in a shadow root, and `organizer/styles/shared.css` is adopted into every root through `ConsoleShadowStyles` (`organizer/ui/shadow-styles.ts`).
- **Tokens today:** the only shared file is `shared/styles/m3-sys.css` (`--md-sys-state-*`, `--md-sys-motion-*`, 91 uses). The organizer console already has role tokens, a global focus ring and a 48 px target. The fan app mostly uses tokens that predate its role layer: `--color-*` 598 times, `--step-*` 245, `--radius-*` 105.
- **Dependencies:** no Material library is installed; all tokens are hand-written. Colours are `oklch()`, and lint forbids hex, `rgb()` and `hsl()`.
- **Sources:** values come from m3.material.io (read with Playwright), `material-components/material-web` token files and `androidx/compose/material3` tokens, which carry the Expressive values. Stylelint facts come from its 18.0.0 changelog and rule documentation.

## Goals / Non-Goals

**Goals:**

- A block cannot undo a shared layer without a written reason.
- One token vocabulary across the fan app and the organizer console.
- Material 3 values wherever Material 3 defines one and no spec of ours says otherwise.

**Non-Goals:**

- Admin and reception. They keep their own tokens and only inherit the upgraded stylelint and the removal of `stylelint-use-logical`.
- Colour palette changes. Colour role values stay as they are; only their names and the higher-contrast set change.
- Component redesigns beyond the sizes in the specs. The snack bar, the FAB menu and the four button variants keep their specified look.
- Adopting `@material/web` or Material Theme Builder output. Neither fits oklch tokens and shadow-root components without a rewrite.
- Spring-based animation changes. The tokens are renamed only.

## Decisions

### Core stylelint rules, scoped by file path

Stylelint 18 can express every new restriction, so no new `cube/*` rule is written. Scope: `src/components/**`, `src/routes/**`, `shared/ui/**`, `src/styles/button.css`, and `organizer/**` except `organizer/styles/**`, through `overrides` in `stylelint.config.js`.

| Goal | Rule | Value |
|---|---|---|
| No margins, fonts or focus outlines in a block | `property-disallowed-list` | `/^margin/`, `/^font(-family\|-size\|-weight\|-style)?$/`, `line-height`, `letter-spacing`, `/^outline/`, plus the base config's `z-index` |
| No values that repeat the reset | `declaration-property-value-disallowed-list` | `/^padding/`: `0`; `list-style`: `none`; plus the base config's entries |
| Only role tokens | `declaration-property-custom-property-allowed-list` | colour properties: `--md-sys-color-*`, `--color-brand-*`, `--color-stage-*`, status colours; `border-radius`: `--md-sys-shape-*`; `box-shadow`: `--md-sys-elevation-*`, `--glow-*`; `/^(padding\|gap)/`: `--space-*`; local `--_*` always |
| Raw shadows | `declaration-property-value-allowed-list` | `box-shadow`: `none` or a `var()` |
| Undefined tokens | `no-unknown-custom-properties` with `referenceFiles` | replaces `cube/no-undefined-color-token` |
| Logical properties | `property-layout-mappings: flow-relative` | `ignoreProperties` keeps today's `width`/`height` exception; replaces `stylelint-use-logical` |
| Disable comments | `reportNeedlessDisables`, `reportDescriptionlessDisables`, `reportUnscopedDisables` | all on |
| Block size | `cube/block-max-lines` | 100 |

An `overrides` entry replaces a rule's value rather than merging it, so the base config's entries are repeated there.

*Alternatives:* new `cube/block-no-*` rules, or `stylelint-no-restricted-syntax` queries on the `@layer` at-rule. Both add code or a dependency for checks the file layout already allows.

**Spikes in the first task, each with a stated fallback.**

- `cube/require-token-variables` may be replaced by the experimental `value-type-custom-property-required-list`. If that reports different problems on the rule's existing test cases, the `cube/` rule stays.
- `no-unknown-custom-properties` considers the same source and `referenceFiles`. A component reading a custom property defined by another component would be a false positive. If so, those properties move to tokens or the file gets a described disable.

**Plugin rules that stay:** core has no equivalent for `require-layer`, `layer-order`, `exception-data-attr`, `no-visual-in-composition`, `utility-single-property`, `block-require-scope`, `one-block-per-file`, `prefer-where-in-reset`, `data-attr-naming`, `prefer-vi-over-vw`, `require-container-name`, `prefer-color-mix`, `block-max-lines`. Their tests must pass on stylelint 18, which removed `context.fix`.

### Tests are the contract for the lint rules

`stylelint-plugin-cube-css/test/` gains a suite that runs the real `stylelint.config.js` over fixtures, including the original defect: a list with `margin: 0` inside `.flow`. CSS architecture gets no spec because users cannot observe it; a spec could only restate this config. `AGENTS.md` keeps pointing at `stylelint.config.js`.

### Suppressions are the work list

Rules go on in the first PR with `stylelint --suppress`, and `stylelint-suppressions.json` is committed. A new violation fails immediately. A file's entry shrinks as it is migrated, and an empty file is the completion condition. `lint:css` has no flag to add because the default location is used.

The feature is marked experimental in stylelint's documentation. The exact version stays pinned, and the worst case is regenerating one JSON file, so the risk is low.

### Exceptions go through described disable comments

Margins are banned outright, with no allow-list. Anything the platform forces, such as an artist name sized to its lane (`live-highway`) or a focus style drawn by a field around its input (`console-field`, `venue-field`, `data-list`), uses `stylelint-disable-next-line` with a reason, which `reportDescriptionlessDisables` requires. Reviewers can then see each exception in the diff.

A block that needs a margin between its children sets `--flow-space` or `gap` instead.

### Token names

| Family | Name | Lives in |
|---|---|---|
| Type style | `--md-sys-typescale-<role>-<size>` (a `font` value), `-tracking`, and `-emphasized` variants | shared |
| Typeface | `--md-ref-typeface-plain`, `--md-ref-typeface-brand` | plain shared; brand per app |
| Colour role | `--md-sys-color-<role>` | per app |
| Shape | `--md-sys-shape-corner-<step>` | per app |
| Elevation | `--md-sys-elevation-level<n>` | shared; shadow colour per app |
| State, motion | `--md-sys-state-*`, `--md-sys-motion-*` (springs join here) | shared |
| Focus | `--md-sys-state-focus-indicator-thickness`, `-outer-offset` | shared; colour per app |
| Target | `--md-sys-target-size` (48 px) | shared |
| Spacing | `--space-3xs` to `--space-3xl` | per app, same values |
| No Material 3 meaning | `--color-brand-*`, `--color-stage-*`, status colours, `--glow-*`, component `--_*` | per app |

The fan app's `--color-text-muted` merges into `on-surface-variant`, because Material 3 has no third text tier.

*Alternatives:* Utopia's names (`--step-*`) cannot tell `title-medium` from `body-large`, which share a size and differ in weight and tracking. Unprefixed names (`--type-title-large`) would add a third form next to the existing `--md-sys-*`.

### Type styles are utility classes

`shared/styles/m3-typescale.css` defines `.md-typescale-<role>-<size>` and `-emphasized` in the `utility` layer, each setting `font` and `letter-spacing`. Templates add the class; a block sets no font at all. The organizer gets the classes through `shared.css`, so they reach every shadow root.

`font` and `letter-spacing` are two properties, so `cube/utility-single-property` gets one allowance for `.md-typescale-*`: the token cannot be expressed in one declaration.

Default mapping for migration, adjusted by what the text is, not only its current size:

| Today | Becomes |
|---|---|
| Route and page titles (`display` / `step-2`) | `headline-small` |
| Empty-state and section titles (`display` / `step-0`, `step-1`) | `headline-small` or `title-large` |
| Step titles (`step-1` / 600) | `title-large` emphasized |
| `step-0` | `body-large`, or `title-medium` when weight is 600 |
| `step--1` | `body-medium`, or `label-large` in controls and with weight 500 or more |
| `step--2` | `label-small` |

`title-large` deliberately uses the plain typeface, unlike Material 3's default of brand: the agreed assignment is brand for display and headline only, and Material 3 itself advises caution with expressive fonts in titles.

### Typefaces

Both apps load `Noto Sans JP:wght@100..900` from Google Fonts (`display=swap`), and the fan app also loads `Righteous`. `--md-ref-typeface-plain` is `"Noto Sans JP", "Hiragino Sans", "Yu Gothic UI", system-ui, sans-serif`. In the fan app `--md-ref-typeface-brand` prepends `Righteous`; in the organizer console it equals `plain`. `font-synthesis-weight: none` stops the browser faking bold on Righteous, so an emphasized headline stays 400 in Latin letters and becomes heavier in Japanese.

`button.css`'s Outfit becomes the plain typeface, since Righteous's missing bold was the reason for it.

The organizer console moves to Noto Sans JP because its earlier system-font choice records no reason (`redesign-organizer-console` only names the stack), and today it looks different on Windows and on a Mac, the problem the fan app is fixing. It takes no brand typeface: its spec describes a calm work tool and limits brand colour to the primary action, focus and the logo, and Righteous would set Latin letters in concert and artist names in a decorative face. `organizer.html` already allows Google Fonts in its CSP. Noto Sans JP keeps the tabular figures the console requires: measured at 14 px, `1111` and `0000` are both 32 px wide, with and without `tabular-nums`. `organizer/guide/guide.html` copies the console's font stack and changes with it.

This also records why type is fixed rather than fluid: `refactor-shared-ui-design-system` chose fluid scales as "more capable", and `redesign-organizer-console` amended that for the console because members compare numbers across windows and Material 3 adapts layout, not text size, across window classes. That reasoning holds for the fan app too, where body sizes differ by under 0.5 px across phone widths.

*Alternatives:* keeping Poppins for Latin text with Noto Sans JP behind it would mean two text faces in one line, for no agreed benefit.

### Focus ring colour is ours, not Material 3's `secondary`

The size follows Material 3: 3 px, offset 2 px. The colour does not: the organizer spec reserves brand magenta for focus, and the fan app's outlines already use `--color-brand-primary`. The fan `primary` role is darkened to carry a white label, so on dark navy it could fall below 3:1; the fan app therefore points the ring at the brighter brand colour. The ring colour is one per-app token.

### Sheets use `surface-container`, not Material 3's `surface-container-low`

The fan app defines `surface-container-low` as equal to `surface`, so the Material 3 value would erase the separation from the page. Sheets keep today's lighter tier. Every other sheet value follows Material 3: 28 px corner, 32 × 4 px handle in a 48 px area, level 1, 640 px maximum width.

### Sheet heading is a bindable

`<bottom-sheet heading.bind="...">` renders an `h2` with the type style and points `aria-labelledby` at it, replacing per-sheet `aria-labelledby` ids and title classes. A bindable is enough: existing headings are plain text.

### One `<list-item>` in the fan app only

`src/components/list-item/` replaces the settings row markup and the All Nearby filter row. The organizer console keeps `organizer/ui/list-item`, which already has the same measurements, because it renders in a shadow root with native `<slot>`s. Merging them would mean supporting both slot systems for no visible gain.

### 48 px targets without visible growth

A control whose visible shape must stay small (the 36 px compact button, the hype dots, chips) extends its target with a transparent `::after` centred on the control, as the organizer console does through `--md-target-size`. A control that may simply grow does so. The hype dots need checking at 320 px: four 48 px targets take 192 px, which leaves 128 px for the artist name.

### Breakpoints are not linted

`@container` conditions cannot read custom properties, and core stylelint has no rule that restricts their values. Only window-level layouts are bound by the breakpoints, the organizer already complies, and the fan app has none today. A review criterion in `AGENTS.md` is enough. The fan app's unused `--container-*` tokens are deleted.

### Delivery: a sequence of PRs, not one

`AGENTS.md` says one PR per repository. This change is a deliberate exception: the renames alone touch every stylesheet, and a single PR could neither be reviewed nor be rebased across other work. Each task group is one PR citing this change, released and checked before the next. The renames are one mechanical commit per token family so that the `pre-push-review` skill can exclude them. Every group leaves the app working, so the sequence can pause at any point.

## Risks / Trade-offs

- **Every fan screen changes at once in small ways** → groups land separately, each with regenerated baselines and Playwright runs of the screens it touches. There are no real users yet (root `CLAUDE.md`), so visible churn costs little.
- **Rebasing concurrent changes across renames** → mechanical commits are scripted, so a conflicting branch can re-run the script instead of resolving by hand. The scripts are kept in the PR description.
- **Noto Sans JP adds transfer and a visible font swap** → measure LCP and transferred font bytes on `/dashboard` and the organizer concerts screen in production before and after. If LCP worsens by more than 200 ms, fall back to loading only the weights in use (400, 500, 600).
- **Text set in a new typeface wraps differently** → a line of Noto Sans JP is not the same width as the system font, so fixed-height rows may overflow. The Storybook runs at 320 px catch this for storied components.
- **Fixed 14 px body text replaces fluid sizes** → a few places get slightly smaller or larger. The contrast and layout checks run on every story.
- **Splitting 40 stylesheets may stall on large routes** (`discovery-route.css` at 461 lines) → the suppression list makes the remainder visible. If a block cannot reach 100 lines without a component that means nothing on its own, it gets a described disable, and the reason is reviewed in the PR.
- **Bulk suppressions are experimental** → see the decision above.
- **Coverage debt:** modifying a requirement requires `@spec` tests for all its scenarios at archive, and `check-scenario-coverage.py` currently reports about 98 uncovered scenarios for this change, mostly `bottom-sheet` and `live-highway`. Many tests likely exist unannotated. Group 9 annotates them or adds the missing tests.

## Migration Plan

1. Lint rules with suppressions (group 1). No visible change.
2. Shared tokens added beside the old ones (group 2). No visible change.
3. Mechanical renames of colour, shape, motion and state (group 3). No visible change.
4. Type styles and typefaces (group 4), spacing and margins (group 5), focus, targets and elevation (group 6). Visible.
5. Shared components and block splits (groups 7 and 8). Visible.
6. Old tokens deleted when the suppression list is empty (group 9).

Rollback is reverting the PR and cutting a new release; no data or API is involved.

## Open Questions

None.
