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

Task 5.2 found the reset-repeat rule right only for the fan app. The organizer console's reset (`organizer/styles/shared.css`) zeroes margins, not padding or list style, so a console `padding: 0` undoes a browser default; the rule leaves console stylesheets alone. In the fan app, a `padding: 0` on a button or form field cancels the padding `global.css` gives them, not the reset; those keep a described disable.

An `overrides` entry replaces a rule's value rather than merging it, so the base config's entries are repeated there.

*Alternatives:* new `cube/block-no-*` rules, or `stylelint-no-restricted-syntax` queries on the `@layer` at-rule. Both add code or a dependency for checks the file layout already allows.

**Spikes in the first task, each with a stated fallback.**

- `cube/require-token-variables` may be replaced by the experimental `value-type-custom-property-required-list`. If that reports different problems on the rule's existing test cases, the `cube/` rule stays.
- `no-unknown-custom-properties` considers the same source and `referenceFiles`. A component reading a custom property defined by another component would be a false positive. If so, those properties move to tokens or the file gets a described disable.

**Spike outcomes (task 1.3).**

- `value-type-custom-property-required-list` gave a different result on 8 of the 15 `cube/require-token-variables` test cases, because it cannot exempt a layer or limit itself to chosen properties. `cube/require-token-variables` stays.
- `no-unknown-custom-properties` has real false positives on properties set by a template (`--artist-hue`, `--i`, `--n`, the celebration pieces' `--_*`, `--_vt-name`, `--_dot-color`) and by another stylesheet (`--orb-floor`): those carry a described disable. `--page-inline-padding` is resolved by adding `organizer-shell.css` to the organizer's `referenceFiles`. Relative `referenceFiles` resolve against the config file: running from a subdirectory reports the same result.
- `no-unknown-custom-properties` also found a real defect: admin stylesheets used `--space-xs` and `--step-1`, which the admin entry never defined. They are now defined.
- `property-layout-mappings` also objects to multi-value `padding`, `margin` and `inset` and to `overflow-*` and `overscroll-behavior-*`, which `stylelint-use-logical` accepted. They are in `ignoreProperties` beside `width` and `height`, so the swap reports nothing new.

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
| Type style | `--md-sys-typescale-<role>-<size>-font`, `-weight`, `-emphasized-weight`, `-size`, `-line-height`, `-tracking` (Material Web's names; no `font` shorthand) | shared |
| Typeface | `--md-ref-typeface-plain`, `--md-ref-typeface-brand`, `--md-ref-typeface-mono` | plain shared; brand and mono per app |
| Colour role | `--md-sys-color-<role>` | per app |
| Shape | `--md-sys-shape-corner-<step>` | per app |
| Elevation | `--md-sys-elevation-level<n>` | shared; shadow colour per app |
| State, motion | `--md-sys-state-*`, `--md-sys-motion-*` (springs join here as `--md-sys-motion-spring-*`) | shared; task 2.2's "spring tokens per app" follows this row, since springs are not app-specific |
| Focus | `--md-sys-state-focus-indicator-thickness`, `-outer-offset` | shared; colour per app |
| Target | `--md-sys-target-size` (48 px) | shared |
| Spacing | `--space-3xs` to `--space-3xl` | per app, same values |
| No Material 3 meaning | `--color-brand-*`, `--color-stage-*`, status colours, `--glow-*`, component `--_*` | per app |

The fan app's `--color-text-muted` merges into `on-surface-variant`, because Material 3 has no third text tier.

**Rename mapping applied in group 3.** Colour: `--md-color-*` became `--md-sys-color-*` in both apps, app-specific roles included (snack, menu surface, the console's status containers), so colour has one prefix. The fan app's role-like tokens went to the role that already aliased them: `surface-base` to `surface`, `surface-raised` to `surface-container`, `surface-overlay` to `surface-container-high`, `text-primary` to `on-surface`, `text-secondary` to `on-surface-variant`, `border-muted` to `outline`, `border-subtle` to `outline-variant`. `--color-white` has no role and stays beside the brand, stage and status colours. Shape: `--radius-sm`, `-button`, `-card`, `-full` to `--md-sys-shape-corner-small`, `-medium`, `-large`, `-full`. State: uses read `--md-sys-state-*-opacity` as the console does (the number for `opacity`, `calc(... * 100%)` in `color-mix()`); `--md-state-selected` stays fan-local because Material 3 has no selected opacity. Motion: `--transition-fast`, `-normal`, `-slow` to `--md-sys-motion-duration-short3`, `short4`, `medium2`; the springs, easings and durations to the shared `--md-sys-motion-*`, which collapse to 0 ms under reduced motion where the fan copies did not; `--md-duration-instant` (1 ms, still fires `transitionend`) stays fan-local. The organizer guide keeps its own variables.

*Alternatives:* Utopia's names (`--step-*`) cannot tell `title-medium` from `body-large`, which share a size and differ in weight and tracking. Unprefixed names (`--type-title-large`) would add a third form next to the existing `--md-sys-*`.

### Type styles are utility classes

`shared/styles/m3-typescale.css` defines `.md-typescale-<role>-<size>` and `-emphasized` in the `utility` layer, each setting the five longhands `font-family`, `font-weight`, `font-size`, `line-height` and `letter-spacing`. Templates add the class; a block sets no font at all. The organizer gets the classes through `shared.css`, so they reach every shadow root.

The classes set five longhands, not the `font` shorthand: the fan app sets `font-feature-settings: "palt"` once on `<html>`, and the shorthand resets every font property it does not name, `palt` included (fan-web-motion-and-typography, design D8, frontend#981). `stylelint.config.js` therefore allows `cube/utility-single-property` up to five for `m3-typescale.css` only. Nothing in either app sets the `font` shorthand.

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

The organizer console moves to Noto Sans JP because its earlier system-font choice records no reason (`redesign-organizer-console` only names the stack), and today it looks different on Windows and on a Mac, the problem the fan app is fixing. It takes no brand typeface: its spec describes a calm work tool and limits brand colour to the primary action, focus and the logo, and Righteous would set Latin letters in concert and artist names in a decorative face. `organizer.html` already allows Google Fonts in its CSP. Noto Sans JP keeps the tabular figures the console requires: measured at 14 px, `1111` and `0000` are both 32 px wide, with and without `tabular-nums`. `organizer/guide/guide.html` copies the console's font stack and changes with it. The console's two monospaced values (`copy-field`, `reception-tab`) keep their face through a `.typeface-mono` utility over `--md-ref-typeface-mono`, because blocks no longer set fonts.

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

### Navigation labels at 320 px (found in task 4.2)

At 320 px the four navigation tabs share the width with the FAB notch, and at label-medium (12 px) "Timetable" and "Discovery" touch. Group 4 sets the labels at label-small (11 px), today's size; task 7.4, which moves them to label-medium with the 64 px bar, has to make them fit at 320 px.

### 48 px targets without visible growth

A control whose visible shape must stay small (the 32 px compact button, the hype dots, chips) extends its target with a transparent `::after` centred on the control, as the organizer console does through `--md-target-size`. A control that may simply grow does so. The hype dots need checking at 320 px: four 48 px targets take 192 px, which leaves 128 px for the artist name.

### Breakpoints are not linted

`@container` conditions cannot read custom properties, and core stylelint has no rule that restricts their values. Only window-level layouts are bound by the breakpoints, the organizer already complies, and the fan app has none today. A review criterion in `AGENTS.md` is enough. The fan app's unused `--container-*` tokens are deleted.

### Style audit after group 5 (2026-11-09)

After group 5, a read-only audit of every stylesheet and template in both apps
(fan components and shared UI, fan routes, organizer console) looked for styles that
are inconsistent, duplicated or unnecessary. It found four kinds of problem:

- **Defaults that blocks undo.** `global.css` padded every `<button>` although only two
  buttons used it (removed in group 5); the field rule is replaced by every text field;
  `:where(svg)` fills every SVG, so hand-written icons draw as solid shapes (the
  inline-error "i" is a disk); block-level `background: transparent` and `border: none`
  remove the hover layer and the high-contrast borders the global layer gives buttons.
  The organizer reset zeroes only margins, so about 35 console declarations reset
  lists, fieldsets, buttons and links one by one.
- **The same UI built more than once.** Five copies of the text field in fan routes, five
  filter chips, eight panel cards, four definition-list summaries, six tinted badges,
  about thirteen text links in three colours, two bottom banners of about 60 identical
  lines, four compact-button size overrides, two byte-identical organizer sale-editor
  stylesheets, four organizer icon-button, menu and full-bleed copies, and four looks
  for an empty or error state.
- **Values that should be tokens**: local variables that rename a token, `50%` radii
  beside `--md-sys-shape-corner-full`, raw durations that miss the reduced-motion
  collapse, the console's `--md-target-size` and `--md-elevation-*` beside the shared
  `--md-sys-*` ones, and repeated literals (48 px, 56 px, 64 px, 36rem).
- **Dead CSS**: unused utilities and keyframes (about 100 lines), a 43-line copy of the
  settings switch in the consent route, and rules for classes no template uses.

Two console defects came out of it: the snack bar reads `--bottom-banner-height` while
the shell sets `--bottom-banner-clearance`, so a snack can cover the floating button;
and `.main { outline: none }` hides the page area's focus ring.

**Decisions.** Both apps share one foundation: the reset, compositions (`flow`,
`stack`, `cluster`, `center`, `wrapper`, and a full-bleed one), `visually-hidden` and the
state layer move to `shared/styles/`, as the type scale did, so a console component's
shadow root gets the same layers as the fan app. A UI pattern used by two or more blocks
becomes one shared block. Where the copies look different, the shared block takes the
Material 3 value (the owner chose this over keeping the most common look): one link
colour role, `outline-variant` for card and divider lines, the scrim token behind
dialogs and sheets, hover, focus and press drawn by one state-layer mechanism. Material 3 scales
no pressed component (foundations/interaction/states/applying-states: press is a
ripple overlay), so the press scales go; a common button keeps the M3 pressed
corner morph toward square. Each PR that changes how something looks lists the change with before and
after images.

**How "no visible change" is checked.** Group 5 recorded every element's box at the end
of each functional and onboarding e2e test, before and after, with web fonts blocked so
text widths match, and compared them by element. Groups 10–12 use the same record,
kept as an opt-in e2e fixture.

**Order.** 10 (defects) → 11 (one foundation, no visible change) → 12 (shared blocks,
visible) → 6 → 7 → 8 → 9. Group 12 touches the same controls as 6 and 7, so it goes
first; it ships one PR per block family rather than one for the group.

### Delivery: a sequence of PRs, not one

`AGENTS.md` says one PR per repository. This change is a deliberate exception: the renames alone touch every stylesheet, and a single PR could neither be reviewed nor be rebased across other work. Each task group is one PR citing this change, and the PRs merge in group order, each released and checked in production. The next group's work starts once the previous PR has merged, while that release is still being checked: it is rebased onto `main` before its own PR, so a defect found in production is fixed on `main` first and reaches it there. The full Storybook and e2e suites run in CI; locally a group runs the stories and e2e specs of what it touches. The renames are one mechanical commit per token family so that the `pre-push-review` skill can exclude them. Every group leaves the app working, so the sequence can pause at any point.

### Scenarios verified without a test of their own (task 9.1)

`check-scenario-coverage.py` accepts a scenario that no automated test can carry when a line here says how it is verified. The first three are rules for editing the brand-expression registry, a table in the i18n spec; the registry's contents and its invariants are asserted by `test/locales/brand-expressions.node.spec.ts`, but what a future edit may do to the table is checked when the table is reviewed. The fourth is a rule about every stylesheet at once; `test/styles/window-breakpoints.node.spec.ts` lists every width `@media` query in `src/` and fails on one that is not a Material 3 breakpoint, in place of exercising a screen, because no fan screen reflows with the window's width.

@spec-manual components/infrastructure/fan/web/global/i18n "Adding a new brand expression" -- reviewed in the spec change that edits the registry table; the app's registry is asserted by test/locales/brand-expressions.node.spec.ts
@spec-manual components/infrastructure/fan/web/global/i18n "Removing a graduated expression" -- reviewed in the spec change that edits the registry table
@spec-manual components/infrastructure/fan/web/global/i18n "Registry SHALL NOT include deprecated colloquial terms" -- reviewed in the spec change that edits the registry table
@spec-manual components/infrastructure/fan/web/global/design-tokens "Window width crosses a breakpoint" -- test/styles/window-breakpoints.node.spec.ts scans every width @media query in src/ for the Material 3 breakpoints (600, 840, 1200, 1600 px); the two height-and-width queries on page-header and Discovery are the spacing exception the requirement allows

### Production check after the last release (task 9.3, 2026-11-12, v1.166.0)

The deployed version is v1.166.0 (the fan app's `config.json` `releaseVersion`, and the images of `fan-web-app` and `organizer-console-web-app`, both rolled out with one ready replica; `kubectl rollout status`, read only). Playwright opened `/dashboard` (as a guest and signed in), `/discovery`, `/my-artists`, `/tickets` and `/settings` on the Pixel 7 and iPhone 14 profiles, `/my-artists` and `/dashboard` at 320 px, and the organizer concerts screen on the Pixel 7 profile and at 1440 px: 16 of 16 pages showed no horizontal scroll and no clipped text, drew their text in Noto Sans JP, and raised no console error or failed request. At 320 px a four-character artist name shows whole, no two navigation labels touch and the centre button covers no tab; a longer name (`Official髭男dism`, 112 px of text in 87 px) is cut with an ellipsis on purpose.

What was emulation, not a physical device:
- The iPhone 14 profile ran in Chromium: WebKit cannot start on the machine. WebKit-specific behaviour is covered by the `webkit-*` projects in CI.
- The signed-in fan and the console member are a fake OIDC user stored under the production key, with every RPC (and PostHog and Last.fm) answered by Playwright route interception; no real sign-in and no write reached production.
- Onboarding was marked complete and the install banner and celebration hidden in advance; the first-run onboarding screens were not exercised.
- No physical phone was used, so the home-indicator area and real touch input were not checked on a device.

## Risks / Trade-offs

- **Every fan screen changes at once in small ways** → groups land separately, each with regenerated baselines and Playwright runs of the screens it touches. There are no real users yet (root `CLAUDE.md`), so visible churn costs little.
- **Rebasing concurrent changes across renames** → mechanical commits are scripted, so a conflicting branch can re-run the script instead of resolving by hand. The scripts are kept in the PR description.
- **Noto Sans JP adds transfer and a visible font swap** → measure LCP and transferred font bytes on `/dashboard` and the organizer concerts screen in production before and after. If LCP worsens by more than 200 ms, fall back to loading only the weights in use (400, 500, 600).
- **Baseline measured before group 4 (2026-11-08, release v1.144.1).** Playwright on Chromium, Japanese locale, cold cache, median of 7 loads from the same machine; the same script is re-run after release. A guest `/dashboard` reports no LCP: its main text is in the home-area sheet, which opens in the top layer with an entry animation, and Chrome emits no LCP candidate. Its FCP stands in, and `/welcome`, the first text-heavy public screen, gives the LCP. The organizer concerts screen needs a member login that no automated run has, so the console's public landing page stands in.

  | Page (device) | LCP | FCP | Font bytes |
  |---|---|---|---|
  | fan `/dashboard`, guest (Pixel 7) | none | 3,640 ms | 44.6 KB |
  | fan `/welcome` (Pixel 7) | 3,564 ms | 3,436 ms | 61.1 KB |
  | organizer `/` (Desktop Chrome) | 2,340 ms | 1,460 ms | 0 |
  | organizer `/` (Pixel 7) | 2,072 ms | 1,240 ms | 0 |

- **After group 4 (2026-11-09, release v1.145.0)**, same script and machine. LCP stays within the 200 ms threshold on every page, so the weight fallback is not needed. Font bytes grow because both apps now download Noto Sans JP: Google Fonts serves it in Unicode-range slices, and a Japanese page fetches the slices for the characters it shows. Fonts are ready about 0.5 s after navigation start, before the first paint.

  | Page (device) | LCP | FCP | Font bytes |
  |---|---|---|---|
  | fan `/dashboard`, guest (Pixel 7) | none | 3,408 ms (−232) | 436.5 KB |
  | fan `/welcome` (Pixel 7) | 3,588 ms (+24) | 3,476 ms | 340.6 KB |
  | organizer `/` (Desktop Chrome) | 1,928 ms (−412) | 1,200 ms | 271.2 KB |
  | organizer `/` (Pixel 7) | 1,992 ms (−80) | 1,200 ms | 270.8 KB |

- **Text set in a new typeface wraps differently** → a line of Noto Sans JP is not the same width as the system font, so fixed-height rows may overflow. The Storybook runs at 320 px catch this for storied components.
- **Fixed type styles replace the fan app's fluid sizes** → body text settles at 16 px and most small text at 14 px, so some text gets slightly larger or smaller. The organizer console's sizes do not change. The contrast and layout checks run on every story.
- **Splitting 40 stylesheets may stall on large routes** (`discovery-route.css` at 461 lines) → the suppression list makes the remainder visible. If a block cannot reach 100 lines without a component that means nothing on its own, it gets a described disable, and the reason is reviewed in the PR. Group 8 left two such blocks:
  - `src/components/bottom-sheet/bottom-sheet.css`: the popover, its backdrop and the scroll area are one closing mechanism. The backdrop fades on the scroll area's timeline, and the snap points, the dismiss area and the opening keyframes only work when they agree. The scroller alone means nothing; the sheet's surface is already its own block (`sheet-surface`).
  - `src/components/live-highway/laser-beams.css`: the beam overlay, its shape, the two bright edges at its tip (pseudo-elements, which cannot leave the block) and the scroll range that makes it reach the card exactly only mean something together.
  
  Splitting the timetable's day row (date group, lane grid, concert lane) into components doubled the window spec's render time (2.1 s to 4.4 s against a 5 s limit), so its markup stays as it is and only its rules moved into separate CSS blocks.
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
