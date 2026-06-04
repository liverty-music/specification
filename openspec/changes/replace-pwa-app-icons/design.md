## Context

The finalized brand icon set arrives as `frontend/favicon.zip` (a RealFaviconGenerator export):

| File | Size | Notes |
|------|------|-------|
| `favicon.svg` | 6.7 MB | **Not vector** — a single 1528×1528 PNG embedded as base64, zero `<path>` elements |
| `favicon-96x96.png` | 21 KB | browser-tab favicon |
| `favicon.ico` | 15 KB | legacy / implicit `/favicon.ico` |
| `apple-touch-icon.png` | 66 KB | iOS home screen, 180×180 |
| `web-app-manifest-192x192.png` | 74 KB | PWA install |
| `web-app-manifest-512x512.png` | 457 KB | PWA install + maskable |
| `site.webmanifest` | 448 B | generic boilerplate (`"MyWebSite"`, white theme, 2 icons) |

Current state in `frontend/public/`: a real 440 B hand-authored `favicon.svg`, a 447 B `apple-touch-icon.svg`, and 593 B / 2.2 KB placeholder PWA PNGs at `icons/icon-192x192.png` and `icons/icon-512x512.png`. The head links live in `frontend/index.html`; the PWA manifest is the carefully customized `frontend/public/manifest.webmanifest`.

## Goals / Non-Goals

**Goals:**
- Present the finalized brand mark in browser tab, iOS home screen, and Android/PWA install.
- Keep transfer size small and Core Web Vitals unaffected.
- Preserve all existing manifest customization (`share_target` ticket-email import, `lang: ja`, themed colors, maskable variant).
- Make the smallest set of edits that achieves the above.

**Non-Goals:**
- Producing a true vector SVG of the new logo (would require a designer re-export; out of scope here).
- Migrating asset paths to a `/icons/` subtree per the export's default snippet.
- Adopting the export's `site.webmanifest` (generic boilerplate; rejected).
- Any backend, proto, or runtime JS change.

## Decisions

**1. PNG/ICO favicon — drop the SVG favicon.**
The exported `favicon.svg` is a raster wearing an `.svg` extension (1528×1528 PNG, base64-embedded, 6.7 MB). It carries none of the scalability benefit of a true vector but inflates transfer size ~15,000×. Browsers render favicons at ≤180 px, so a 96 px PNG plus a multi-resolution ICO is sufficient. We therefore delete `favicon.svg` rather than attempt to optimize the embedded raster.
- *Alternative considered:* downscale + re-embed the raster into a ~tens-of-KB SVG. Rejected — strictly worse than PNG (still raster, extra base64 overhead, no benefit).
- *Alternative considered:* keep an SVG favicon. Rejected — the new asset is not vector, so there is nothing to keep.

**2. Preserve the existing manifest; edit only the `icons` array.**
The export's `site.webmanifest` is generic boilerplate and would destroy the existing `share_target`, `lang: ja`, and themed configuration. We keep `frontend/public/manifest.webmanifest` and only update its `icons`: remove the two SVG entries (`/favicon.svg`, `/apple-touch-icon.svg`), point apple-touch at the new `/apple-touch-icon.png`, and keep the 192/512 entries (including the maskable 512) by saving the new PWA PNGs under the existing filenames.

**3. Save new PWA PNGs under the existing filenames.**
`web-app-manifest-192x192.png` → `public/icons/icon-192x192.png`, `web-app-manifest-512x512.png` → `public/icons/icon-512x512.png`. This keeps the manifest's `/icons/icon-*` `src` paths valid with only a byte swap and avoids touching the 192 and both 512 entries' paths.

**4. Keep the public-root file layout.**
The export snippet assumes everything under `/icons/` (including the manifest). We keep root-level placement (`/favicon-96x96.png`, `/favicon.ico`, `/apple-touch-icon.png`, `/manifest.webmanifest`) to minimize edits to `index.html` and avoid a path migration.

**5. Unify `theme-color` to `#1a1333`.**
`index.html` declares `#1a1a3a`; the manifest declares `#1a1333`. The manifest drives PWA/start-url theming and is treated as the source of truth, so `index.html` is aligned to `#1a1333`.

Resulting `index.html` head:
```html
<meta name="theme-color" content="#1a1333">
...
<link rel="icon" type="image/png" href="/favicon-96x96.png" sizes="96x96">
<link rel="shortcut icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
```

## Risks / Trade-offs

- **No vector favicon → no automatic crisp scaling beyond the supplied raster sizes** → 96 px PNG + multi-res ICO cover all real rendering sizes (≤180 px); negligible in practice.
- **No `prefers-color-scheme` adaptation in the favicon** (an SVG could embed media queries) → the brand mark is designed against a fixed dark background; not required.
- **Frontend visual baselines may flag the new icons** → if any visual test captures the tab/app icon, regenerate baselines per the project's main-branch baseline-refresh process.
- **Stale caches** → favicons are aggressively cached by browsers; the change is non-breaking and resolves on natural cache expiry / hard reload. No mitigation needed for correctness.

## Migration Plan

1. Extract `frontend/favicon.zip` to a temp location.
2. Place/replace assets in `frontend/public/` per Decisions 3–4; remove `favicon.svg` and `apple-touch-icon.svg`.
3. Edit `index.html` head and `manifest.webmanifest` `icons`.
4. Remove `frontend/favicon.zip` from the repo.
5. `make check` in `frontend`.

Rollback: revert the commit; the previous placeholder assets and head links are restored wholesale.

## Open Questions

None.
