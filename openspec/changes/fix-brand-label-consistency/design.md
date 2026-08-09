## Context

Two small, related frontend presentation bugs concern how the product's own name and navigation labels are shown to users.

1. **PWA home-screen label.** `frontend/public/manifest.webmanifest` declares `name: "Liverty Music"` and `short_name: "Liverty"`. Per the Web App Manifest spec, launchers prefer `short_name` for the space-constrained home-screen icon label; on Android it is the primary label and on iOS/iPadOS (16.4+) the manifest `short_name` takes precedence over the legacy `apple-mobile-web-app-title` meta tag (which this app does not set). So the installed icon reads "Liverty" — an abbreviation, not the service name.

2. **Settings header locale inconsistency.** Every main tab route binds its `page-header` to a `nav.*` key, and `nav.*` labels are catalogued as invariant-English Layer B brand expressions (they read "Timetable" / "Discovery" / "My Artists" / "Tickets" in both JA and EN). The Settings route alone binds `title-key="settings.title"`, which is a Layer-A-style localized string ("設定" in JA). On a Japanese-locale device, the Settings header is therefore the only tab header rendered in Japanese, breaking the visual consistency of the tab set.

The `page-header` custom element resolves any `title-key` via the i18n `t` binding; the behavior difference is entirely in which key each route chooses. `nav.settings` already exists and is `"Settings"` in both locales. `settings.title` is referenced only by the Settings header.

## Goals / Non-Goals

**Goals:**
- The installed PWA home-screen icon presents the real service name, not the "Liverty" abbreviation.
- The Settings page header is invariant English "Settings", consistent with sibling tab headers.
- The product name's canonical brand forms are recorded authoritatively so they cannot drift silently.

**Non-Goals:**
- No change to the manifest `name` field (stays "Liverty Music"), icons, theme color, or any other manifest member.
- No change to the `page-header` custom element contract.
- No cleanup of the unrelated `import-ticket-email` route, whose header is a hard-coded Japanese `title="チケットメール取り込み"` (a separate, out-of-scope inconsistency).
- No attempt to re-label already-installed home-screen icons; the OS controls that and only refreshes on re-install.

## Decisions

### Decision 1: `short_name` = "LivertyMusic" (single word, no space)

Set `short_name` to `"LivertyMusic"` rather than `"Liverty Music"`.

- **Why:** Home-screen label truncation is launcher- and glyph-width-dependent (~12–15 chars typical: ~15 on Pixel/stock, ~14 Samsung One UI, ~12 on budget devices, ~16 Nova), not a fixed OS limit. `"LivertyMusic"` is 12 characters and avoids the space that could trigger wrapping or an earlier cut; it also matches `short_name`'s intended role as the space-constrained short form. `"Liverty Music"` (13 chars incl. space) risks "Liverty Musi…" on the narrowest launchers.
- **Alternative considered — keep `name` and `short_name` identical ("Liverty Music"):** rejected for the truncation risk above and because it defeats the purpose of `short_name`.
- **Alternative considered — leave `short_name` "Liverty":** rejected; that is the bug being fixed.

### Decision 2: Settings header switches to `nav.settings`, not a JA→EN edit of `settings.title`

Change the Settings route to `<page-header title-key="nav.settings">`.

- **Why:** `nav.settings` is already the invariant-English Layer B label used by the bottom navigation, so the page header and the nav tab share one source of truth and Settings joins the exact pattern its siblings use. One HTML line changes.
- **Alternative considered — rewrite `settings.title` in the JA locale from "設定" to "Settings":** rejected; it injects an English literal into the localized (Layer A-style) namespace, contradicting the two-layer brand-vocabulary model, and leaves two keys that must be kept in sync.
- **Follow-through:** `settings.title` becomes unreferenced; remove it from both `ja` and `en` translation JSON to avoid a dead key. The `brand-vocabulary` lint enforces `entity.*` parity only, so removing a `settings.*` key is safe.

### Decision 3: Record the product name in the `brand-vocabulary` Layer B catalogue

Add the product name to the Layer B brand-expression catalogue: full form "Liverty Music" (manifest `name`, `<title>`, prose) and EN home-screen short form "LivertyMusic" (manifest `short_name`).

- **Why:** The product name has no protobuf entity backing, so by the two-layer model it is a Layer B brand expression whose canonical forms belong in this spec. Recording it makes "LivertyMusic" the authoritative short form and prevents future re-abbreviation to "Liverty".

## Risks / Trade-offs

- **Already-installed icons keep the old "Liverty" label** → Mitigation: expected OS behavior; the corrected label appears on re-install / new installs. No action available or needed.
- **"LivertyMusic" (12 chars, wide "M") could still truncate on the very narrowest launchers** → Mitigation: accepted; it is materially better than "Liverty Music" and the exact cut point is device-controlled. Correct branding outweighs a marginal truncation edge case.
- **Removing `settings.title` could orphan an external reference** → Mitigation: repo grep confirms the key is used only by the Settings header before removal; the change is verified by `make check` (typecheck + lint) and the Settings header E2E/test.

## Migration Plan

Standard frontend change → PR → merge → GitHub Release → automated prod pin-bump → ArgoCD sync. No data migration. Rollback is a normal revert; the manifest and header changes are stateless. Verify the installed-PWA label and the Settings header render post-release.
