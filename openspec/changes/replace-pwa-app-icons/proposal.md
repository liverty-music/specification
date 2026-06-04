## Why

The current frontend ships placeholder brand icons: a hand-authored 440-byte `favicon.svg`, a tiny `apple-touch-icon.svg`, and 192/512 PNGs that were generated as low-fidelity placeholders. A new, finalized brand icon set is now available (RealFaviconGenerator export) and should replace the placeholders so the browser tab, iOS home screen, and Android PWA install all present the real Liverty Music brand mark.

## What Changes

- Replace the placeholder favicon / apple-touch / PWA icon assets in `frontend/public/` with the finalized brand icon set.
- **Drop the SVG favicon entirely** and serve a PNG + ICO favicon instead. The new "SVG" from the export is a 1528×1528 raster embedded as base64 (6.7 MB, zero vector paths), so it carries none of the scalability benefits of a real vector while badly hurting transfer size. PNG/ICO at the sizes browsers actually render (≤180 px) is sufficient and far lighter.
- Add `favicon.ico` at the public root (legacy browsers, Windows tiles, and the implicit `/favicon.ico` request) — the project currently has none.
- Replace `apple-touch-icon.svg` with `apple-touch-icon.png` (the export's 180×180 PNG).
- Update the PWA web app manifest `icons` array to drop the two SVG entries and point apple-touch + 192/512 PNGs at the new assets, while preserving all existing manifest customization (`share_target`, `lang: ja`, themed colors, maskable variant).
- Unify the brand `theme-color`: `index.html` currently declares `#1a1a3a` while the manifest declares `#1a1333`. Align both to the manifest value `#1a1333`.
- Keep the existing public-root file layout (no migration to a `/icons/` subtree) to minimize churn.

## Capabilities

### New Capabilities
<!-- None — this change refines existing brand-identity behavior. -->

### Modified Capabilities
- `app-shell-layout`: The "Favicon and PWA icons" scenario under the **Brand Identity Elements** requirement is refined to (a) deliver the browser-tab favicon as PNG + ICO rather than requiring an SVG, and (b) require the HTML `theme-color` meta to match the web app manifest `theme_color`.

## Impact

- `frontend/public/` — icon asset files (favicon, apple-touch, 192/512 PWA icons) added/replaced/removed.
- `frontend/public/manifest.webmanifest` — `icons` array updated; other fields unchanged.
- `frontend/index.html` — `<head>` icon `<link>` tags and `theme-color` meta updated.
- `frontend/favicon.zip` — source archive removed after extraction.
- No backend, proto, or API changes. No runtime/JS behavior change beyond static asset delivery.
