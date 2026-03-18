## 1. Remove unmatched dimming

- [x] 1.1 Remove `.event-card:not([data-matched]) .artist-logo { filter: brightness(0.35) grayscale(0.8); }` rule from `event-card.css`
- [x] 1.2 Remove `.event-card:not([data-matched]) .artist-name { opacity: 0.6; }` rule from `event-card.css`

## 2. Center-align card content

- [x] 2.1 Add `align-items: center` to `.event-card` flex container in `event-card.css`

## 3. Increase text fallback font size

- [x] 3.1 Change `.artist-name` font-size from `clamp(12px, 5cqi, 24px)` to `clamp(14px, 8cqi, 32px)` in `event-card.css`

## 4. Scale logo with cqi

- [x] 4.1 Change `.artist-logo` `max-block-size` from `3rem` to `25cqi` in `event-card.css`

## 5. Verify

- [x] 5.1 Run `make check` (lint + test) — pre-existing failures only (style.bind grep in dashboard-route.html)
