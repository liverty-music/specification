## 1. Extract and place assets

- [x] 1.1 Extract `frontend/favicon.zip` to a temp location
- [x] 1.2 Copy `favicon-96x96.png` → `frontend/public/favicon-96x96.png`
- [x] 1.3 Copy `favicon.ico` → `frontend/public/favicon.ico`
- [x] 1.4 Copy `apple-touch-icon.png` → `frontend/public/apple-touch-icon.png`
- [x] 1.5 Copy `web-app-manifest-192x192.png` → `frontend/public/icons/icon-192x192.png` (overwrite placeholder, keep filename)
- [x] 1.6 Copy `web-app-manifest-512x512.png` → `frontend/public/icons/icon-512x512.png` (overwrite placeholder, keep filename)
- [x] 1.7 Delete `frontend/public/favicon.svg` and `frontend/public/apple-touch-icon.svg`
- [x] 1.8 Do NOT copy the export's `site.webmanifest` (generic boilerplate, rejected)

## 2. Update HTML head

- [x] 2.1 In `frontend/index.html`, change `theme-color` meta from `#1a1a3a` to `#1a1333`
- [x] 2.2 Replace the `<link rel="icon" ... favicon.svg>` and `<link rel="apple-touch-icon" ... apple-touch-icon.svg>` tags with: PNG `rel="icon"` (96x96), `rel="shortcut icon"` (favicon.ico), and `rel="apple-touch-icon"` (apple-touch-icon.png); keep the manifest link
- [x] 2.3 Update `src/sw.ts` push-notification `icon`/`badge` (were `/favicon.svg`) to PNG assets — `/icons/icon-192x192.png` and `/favicon-96x96.png` — so they don't 404 after SVG removal

## 3. Update web app manifest

- [x] 3.1 In `frontend/public/manifest.webmanifest`, remove the `/favicon.svg` icon entry
- [x] 3.2 Replace the `/apple-touch-icon.svg` entry with `/apple-touch-icon.png` (180x180, type image/png)
- [x] 3.3 Verify the `/icons/icon-192x192.png` and both `/icons/icon-512x512.png` (incl. maskable) entries remain unchanged
- [x] 3.4 Verify `share_target`, `lang`, `name`, `short_name`, `theme_color`, `background_color` are untouched

## 4. Cleanup and verify

- [x] 4.1 Remove `frontend/favicon.zip` from the repo
- [x] 4.2 Run `make check` in `frontend` (lint, types, tests)
- [x] 4.3 If frontend visual baselines capture the icon, regenerate baselines per the main-branch baseline-refresh process
- [x] 4.4 Manually verify favicon in browser tab, and PWA install icon (DevTools → Application → Manifest shows new icons, no 404s)

## 5. Ship

- [x] 5.1 Open frontend PR (Conventional Commits, body + `Refs: #<issue>`), drive CI green, merge to main
- [x] 5.2 Cut a frontend GitHub Release (retag → prod AR) to trigger the automated prod pin bump → ArgoCD sync
- [x] 5.3 Verify the new icons are live on `dev.liverty-music.app` (and prod once rolled out)
