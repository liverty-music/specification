## 1. Icon sizing and fallback (frontend)

- [x] 1.1 Give every `<svg-icon>` that is not set inside running text an explicit size (`size="md"` where it relied on 1.25rem, or its intended step), so the next task changes no rendered size except the seven intended ones (design D1, Migration). Verify `make check` and that the regenerated Storybook baselines in the pinned container (`visual-baselines` skill) show no change at this step
- [x] 1.2 Make the host size the icon size (`--icon-size`, default `1em`, `<svg>` at 100%, `size` steps set `--icon-size`), remove the `default-case` glyph, add `mail` (design D1, D2). Verify `svg-icon` stories for components/infrastructure/fan/web/global/ui-primitives:
  - "Icon rendering by name": an unknown name renders no `<svg>`;
  - "Default size follows the text": an icon inside text matches the text's font size;
  - "Size variants";
  - "Size from a stylesheet": a host `inline-size` / `--icon-size` reaches the `<svg>`;
  - "Icon set coverage": includes `mail`;
  - "Color inheritance".

  Then regenerate the baselines in the pinned container and review each diff in the PR (the seven stylesheet sizes now apply)
- [x] 1.3 Check the screens with changed icons at 375 px with Playwright against a local build (`/passkey-recovery` sent state, `/verify/callback`, Settings, consent, discovery) and attach screenshots to the PR

## 2. Status colors (frontend)

- [x] 2.1 Set `--color-success` to `oklch(72% 0.17 160deg)` and move the call sites in design D3 to their meaning's token. Verify a token test for components/infrastructure/fan/web/global/design-tokens "Success is not the brand accent" (OKLab distances ≥ 0.1 to the brand accent and each stage color) plus the contrast pairs in design D4, and story or fixture assertions for "Done looks the same everywhere" (verify-callback, `/verify-email`, Settings badge use the success color) and "Selected is not shown as done" (Discovery followed check and language check use primary)
- [x] 2.2 Add the stylelint rule that fails on an undefined `--color-*` and replace route-local status literals (`--_green-90`) with `color-mix()` over the token (design D5). Verify a stylelint fixture for "No undefined color" (`--color-accent` fails) and `make check`
- [x] 2.3 Give a paid ticket the success hue (`--journey-hue-paid` = the hue of `--color-success`) and keep the PAID node's label at 4.5:1 (design D3). Verify the token test for "Done looks the same everywhere" checks the PAID hue and the node contrast; release and confirm in prod

## 3. Release

- [x] 3.1 Merge and release; confirm `fan-web-app` rolled out in prod, then open `/verify-email` (a used link), Settings and Discovery on a phone-width window and see the success and selected colors and icon sizes as in the PR screenshots
