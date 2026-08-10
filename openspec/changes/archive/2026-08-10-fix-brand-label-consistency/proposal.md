## Why

The PWA install on Android (and iOS) shows the home-screen label "Liverty" because the web app manifest's `short_name` is set to the abbreviated word "Liverty" instead of the real service name. Separately, the Settings page header is the only main tab whose header switches by locale (renders "設定" in Japanese) while every sibling tab page (Timetable, Discovery, My Artists, Tickets) renders an invariant English brand label. Both are user-visible inconsistencies in how the product's own name and navigation labels are presented.

## What Changes

- Change the PWA manifest `short_name` from `"Liverty"` to `"LivertyMusic"` so the home-screen icon label reads the correct service name. The `name` field stays `"Liverty Music"`. `"LivertyMusic"` (12 chars, no space) is chosen to minimize home-screen label truncation, which is launcher/width dependent (~12–15 chars) rather than a fixed OS limit.
- Change the Settings route header to render the invariant English brand label "Settings" (via the existing `nav.settings` key, which is already `"Settings"` in both JA and EN locales) instead of the locale-switched `settings.title`. This aligns Settings with its sibling tab pages, which all bind `title-key="nav.*"`.
- Catalogue the product name as a Layer B brand expression in `brand-vocabulary` so the canonical home-screen (`LivertyMusic`) and full (`Liverty Music`) forms are authoritative and cannot drift silently.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `app-shell-layout`: the web app manifest requirement gains explicit canonical values — `name` = "Liverty Music" and `short_name` = "LivertyMusic" — so the installed home-screen label presents the correct service name.
- `settings`: the fixed Settings page header SHALL render the invariant English brand label "Settings" (the Layer B navigation label), consistent with sibling tab pages, rather than a locale-switched title string.
- `brand-vocabulary`: the Layer B brand-expression catalogue gains the product name (full form "Liverty Music" / EN home-screen short form "LivertyMusic") and affirms the bottom-navigation / page-header tab labels as invariant-English Layer B expressions.

## Impact

- Frontend only. No backend, proto, or infrastructure changes.
- `frontend/public/manifest.webmanifest` — `short_name` value.
- `frontend/src/routes/settings/settings-route.html` — `page-header` `title-key`.
- `frontend/src/locales/{ja,en}/translation.json` — `settings.title` becomes unreferenced and MAY be removed.
- Ships via the standard frontend release → prod pin-bump path. The manifest change takes effect on next PWA install / manifest re-fetch; already-installed home-screen icons keep their old label until re-installed (OS-controlled).
