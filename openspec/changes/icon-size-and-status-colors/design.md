## Context

See proposal.md - Why. Current state, checked on frontend `main` (2026-10-24):

- **Sizing.**
  - `svg-icon` sizes its inner `<svg>` from a private `--_icon-size` (default 1.25rem). Only `data-size` (the `size` bindable) overrides it.
  - The SVG does not fill the host, so `inline-size` on the host never reaches it.
  - `<svg-icon>` appears 64 times in templates. 15 pass `size`. The other 49 get 1.25rem, whatever their stylesheet says.
- **Stylesheet sizes that do nothing.**

  | Class | Size written |
  |---|---|
  | `passkey-recovery-icon`, `verify-icon` | `--space-xl` |
  | `settings-verification-icon` | 0.875rem |
  | `settings-chevron`, `settings-expand-caret` | 1rem |
  | `consent-row-icon` | 1.1rem |

- **Fallback.** The template's `default-case` draws an info-like "!" circle. The spec says an unknown name renders nothing.
- **Status colors.**

  | Color used | Where | Meaning |
  |---|---|---|
  | `--color-success` | Settings badge, `/verify-email` | done |
  | `--_green-90` (local copy of the success value) | Discovery followed check | selected |
  | `--color-brand-primary` | language check, passkey-recovery "sent" | selected, done |
  | `--color-accent`, defined nowhere | verify-callback success icon | done |

- **Tokens.** `--color-success: oklch(80% 0.18 152deg)`, `--color-brand-accent: oklch(82% 0.22 140deg)` (M3 tertiary, 46 uses), stage colors home 55°, near 195°, away 330°.

## Goals / Non-Goals

**Goals:** one sizing model with no silent no-ops; one token per status meaning; nothing references an undefined color.

**Non-Goals:**

- New icons beyond `mail`.
- Re-theming the brand palette. The brand accent keeps its value.
- Settings row components (frontend#847, done after this change).

## Decisions

### D1. The host's size is the icon's size; the default is `1em`

`svg-icon` sets on its host:

- `inline-size` / `block-size: var(--icon-size, 1em)`;
- the inner `<svg>` at 100%;
- `size="xs…xl"` as a CUBE exception (`data-size`) that only sets `--icon-size` to its step.

A stylesheet can then size an icon with `--icon-size` or with `inline-size` / `block-size` on the host. Inside text an icon matches the text, as Shoelace's `sl-icon` does ("sized relative to the current font size"). Material Web's `md-icon` likewise exposes its size as the public `--md-icon-size`.

| Option | Rejected because |
|---|---|
| Keep 1.25rem as the default, only make the host size apply | An icon next to text still needs a size rule to match the text. That is the drift this change removes. |
| Forbid host sizes with a lint rule | It keeps the trap and moves it to review. |

**Migration.** Before the default changes, every icon that is not set inside running text (navigation, buttons, row leaders, result marks) gets an explicit size, so nothing changes size by accident:

- `size="md"` where it was relying on 1.25rem;
- the step or stylesheet size it was meant to have.

The seven stylesheet sizes above then take effect as written. Each is reviewed against its story or screen.

### D2. An unknown name renders nothing

The `default-case` SVG is removed, as the spec requires. `mail` is added.

A story asserts that an unknown name renders no `<svg>`. A missing icon is then an empty slot a reviewer notices, not a misleading glyph.

### D3. Status meanings map to tokens

| Meaning | Token |
|---|---|
| done / verified | `--color-success` |
| selected | `--md-color-primary` (brand pink) |
| warning | `--color-warning` |
| error | `--color-error` |

**Call sites.**

| Call site | Change |
|---|---|
| verify-callback success | from undefined `--color-accent` to `--color-success` |
| passkey-recovery "sent" | to `--color-success` |
| Discovery followed check | from `--_green-90` to primary. A translucent variant, if needed, is `color-mix()` over the token. |
| language check | already primary |

### D4. Success moves to `oklch(72% 0.17 160deg)`

Distances in OKLab:

| Success value | to brand accent | to stage near (195°) | to other stages |
|---|---|---|---|
| current `oklch(80% 0.18 152deg)` | 0.061 | 0.141 | farther |
| proposed `oklch(72% 0.17 160deg)` | 0.130 | 0.110 | farther |

The proposed value stays green, as event-detail-sheet's PAID requires.

The contrast check runs in a test:

- the success color as text and icon on `--color-surface-base` and `--color-surface-raised`: 3:1 for icons and large text, 4.5:1 where it colors body text;
- the 0.1 OKLab distances.

If a pair fails, the lightness is raised in 2% steps and this decision is updated before merge.

### D5. Undefined `--color-*` fails stylelint

A stylelint rule fails on a `var(--color-*)` that the token files do not define. It runs in `make check`. Route-local `--_*` color literals for a status are replaced by `color-mix()` over the semantic token.

## Risks / Trade-offs

- **[Risk] An icon changes size unexpectedly after D1.** → The migration sets explicit sizes first, and Storybook baselines (regenerated in the pinned container) plus a screen pass show every change. They are reviewed in the PR.
- **[Trade-off]** The PR is wide (49 call sites, 7 baselines). It is split into an icon commit and a color commit for review.
