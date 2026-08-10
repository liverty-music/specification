## 1. PWA manifest short_name

- [x] 1.1 In `frontend/public/manifest.webmanifest`, change `short_name` from `"Liverty"` to `"LivertyMusic"` (leave `name` as `"Liverty Music"` and all other members unchanged)

## 2. Settings header invariant label

- [x] 2.1 In `frontend/src/routes/settings/settings-route.html`, change the header binding from `title-key="settings.title"` to `title-key="nav.settings"` (keep the `data-testid="settings-header"` attribute)
- [x] 2.2 Remove the now-unreferenced `settings.title` key from both `frontend/src/locales/ja/translation.json` and `frontend/src/locales/en/translation.json` (grep-confirm no other reference before removing)

## 3. Local verification

- [x] 3.1 Run `make check` in `frontend` (Biome lint + format + stylelint + typecheck + brand-vocabulary + tests) and confirm it passes
- [x] 3.2 Confirm the Settings header renders "Settings" under both `ja` and `en` locales, and that no existing Settings test/E2E asserts the old "設定" header (update assertions if any reference `settings.title`)

## 4. Ship to production

- [x] 4.1 Open the frontend PR (Conventional Commits, mandatory body + `Refs: #<issue>` footer), wait for all CI checks to pass, address review, and merge
- [x] 4.2 Cut the frontend GitHub Release so the automated prod pin-bump lands the new tag and ArgoCD syncs prod
- [x] 4.3 Verify in production: the served `manifest.webmanifest` reports `short_name: "LivertyMusic"`, a fresh PWA install shows the correct home-screen label, and the Settings header renders "Settings"
