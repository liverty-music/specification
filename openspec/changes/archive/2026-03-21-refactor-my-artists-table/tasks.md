## 1. Delete hype-inline-slider component

- [x] 1.1 Delete `src/components/hype-inline-slider/hype-inline-slider.ts`
- [x] 1.2 Delete `src/components/hype-inline-slider/hype-inline-slider.html`
- [x] 1.3 Delete `src/components/hype-inline-slider/hype-inline-slider.css`

## 2. Rewrite my-artists-route.html

- [x] 2.1 Remove `<import>` of `hype-inline-slider`
- [x] 2.2 Replace `<header class="hype-legend">` + `<ul class="artist-list">` with `<fieldset>` wrapping a `<table>`
- [x] 2.3 Add `<legend class="visually-hidden">` inside `<fieldset>`
- [x] 2.4 Build `<thead>` with sticky `<tr>` containing `<th scope="col">` for: artist name, 👀 チェック, 🔥 地元, 🔥🔥 近くも, 🔥🔥🔥 どこでも！, and visually-hidden "Remove" column
- [x] 2.5 Build `<tbody>` with `repeat.for` on `<tr>` — carry `css="--_vt-name: ...;  --_dot-color: ..."` on `<tr>`
- [x] 2.6 Add `<th scope="row">` with color indicator dot (`aria-hidden="true"`) and artist name (ellipsis truncation)
- [x] 2.7 Add four hype `<td>` cells each containing `<label>` → visually hidden `<input type="radio">` + `<span class="hype-dot" data-active.bind data-level.bind>`
- [x] 2.8 Add delete `<td>` containing `<button type="button" aria-label.bind click.trigger="unfollowArtist(artist)">` with `<svg-icon name="trash" aria-hidden="true">`
- [x] 2.9 Wire `change.trigger="onHypeInput(artist)"` on the radio inputs

## 3. Rewrite my-artists-route.css

- [x] 3.1 Remove `.hype-legend`, `.hype-legend-item` rules
- [x] 3.2 Remove `.artist-list`, `.artist-row`, `.artist-row-content`, `.artist-identity`, `.artist-row-indicator`, `.artist-row-name`, `.dismiss-end` rules
- [x] 3.3 Remove `scroll-snap` related CSS
- [x] 3.4 Add `<fieldset>` reset styles (border, padding, margin)
- [x] 3.5 Add `<table>` styles: `border-collapse: separate`, `border-spacing`, scroll container
- [x] 3.6 Add sticky `<thead>` styles with `backdrop-filter: blur(8px)`
- [x] 3.7 Style `<th scope="row">` (artist name cell: flex, indicator dot, ellipsis)
- [x] 3.8 Style hype `<td>` cells (centered, min tap area)
- [x] 3.9 Move `.hype-slider-dot` base styles, `data-active`/`data-level` dot variant styles, and `@keyframes dot-pulse` from `hype-inline-slider.css` into `@layer block` (under `@scope (my-artists-route)`) — variant styles are nested inside `.hype-dot { &[data-active]... }` which keeps them in block layer; `cube/data-attr-naming` only permits `data-state`/`data-variant`/`data-theme` in exception layer
- [x] 3.10 Add `<td>::before` track line on `.hype-col` cells: `position: absolute; inset-block-start: 50%; inset-inline-start: 50%; inline-size: 100%; block-size: 2px; z-index: 0` — creates a chain of segments connecting adjacent dots (see D3)
- [x] 3.11 Add delete button styles (icon-only, subtle until hover/focus)
- [x] 3.12 Add `view-transition-name: var(--_vt-name)` on `<tr>`

## 4. Update my-artists-route.ts

- [x] 4.1 Remove `checkDismiss` method
- [x] 4.2 Remove `executeDismiss` method
- [x] 4.3 Remove `dismissingIds` Set field
- [x] 4.4 Make `unfollowArtist` public (currently private, now called from template button)
- [x] 4.5 Update `activateSpotlight` target selector from `.artist-list` to the new table target (e.g. `[data-artist-rows]` attribute on `<tbody>`)

## 5. Verify onboarding spotlight target

- [x] 5.1 Add `data-artist-rows` attribute to `<tbody>` in the template
- [ ] 5.2 Confirm spotlight correctly highlights all artist rows (not the thead) in the dev environment

## 6. Lint and tests

- [x] 6.1 Run `make lint` and fix any issues
- [x] 6.2 Run `make test` and fix any broken tests
