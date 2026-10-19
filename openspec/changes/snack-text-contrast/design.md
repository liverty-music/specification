## Context

`shared/ui/snack-bar/snack-bar.css` paints the container as `linear-gradient(to right, var(--_bg-from), var(--_bg-to))`. Info sets the two stops to `--color-brand-primary` (oklch 65% 0.28 350) and `--color-brand-secondary` (oklch 62% 0.25 255). Warning sets oklch 55% / 60% 0.16 75, and error oklch 40% / 45%. An app restyles the whole container through `--snack-bar-container`, which is how the organizer console sets its own colour. axe cannot compute contrast over a gradient, so the Storybook a11y check reports the snack's text as incomplete rather than failing it.

## Goals / Non-Goals

**Goals:**
- Reach 4.5:1 for the white message and for the compact on-container action, at both ends of each gradient, by changing only the snack's container stops.
- Pin the minimum with a test that does not depend on axe.

**Non-Goals:**
- Changing the brand tokens, the FAB, the navigation's line, the filled button or the organizer snack.
- Changing the error gradient, which measures at least 6.1:1 already.

## Decisions

### D1. Darker stops derived from the brand tokens inside the snack bar

Info uses `oklch(from var(--color-brand-primary) 51.5% c h)` and `oklch(from var(--color-brand-secondary) 49% c h)`. Warning uses `oklch(47.5% 0.16 75deg)` on both stops. The lightness values are the highest that keep both the message (white on the stop) and the action (white on 18% white over the stop) at 4.5:1 or more. They were computed with the WCAG relative-luminance formula:

| stop | lightness | message | action |
|---|---|---|---|
| info, brand-primary hue | 51.5% | 4.5 or more | 4.5 or more |
| info, brand-secondary hue | 49% | 4.5 or more | 4.5 or more |
| warning, both stops | 47.5% | 4.5 or more | 4.5 or more |

Deriving from the tokens keeps the snack on the brand hues if the tokens move.

*Alternative:* darken the brand tokens. Rejected: it would change every brand surface, which the user ruled out.
*Alternative:* a neutral dark surface with a brand stripe, or 19px bold text on the current gradients. Both were compared in Storybook. The user chose the darker gradients, and the large-text option wrapped the update message at 360px.

### D2. A contrast check in the snack-bar story

The severity stories (Info, Warning, ErrorSeverity) and UpdateAction read the computed `--_bg-from` and `--_bg-to` of the shown snack, plus the action's computed fill. They composite the fill over each stop on a canvas, compute the WCAG ratio against the computed text colour, and assert at least 4.5. The check runs in Chromium in the existing `storybook` and `storybook-reduced-motion` projects. The screenshots of the changed stories are regenerated in the pinned container.

*Alternative:* rely on axe. Rejected: axe marks text over gradients as incomplete, so a regression would pass.

## Risks / Trade-offs

- **[The snack reads darker than the bright FAB beside it]** The user accepted this after comparing it in Storybook. The hues stay the same, so it reads as the same brand family.
- **[Relative colour syntax support]** `oklch(from …)` is already used across `tokens.css` and component CSS on the same browser targets.
