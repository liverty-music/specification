## Why

The fan Settings screen grew one section at a time, and it now reads as a pile rather than a page. For a signed-in fan the order is preferences, privacy, legal links, then the ticket name form, then the account rows: the fan's own account comes after the legal documents. The Privacy Policy appears twice as identical rows. The analytics toggles are named "分析" and "セッションリプレイ", words a fan does not know, and the replay description calls the recording 匿名化 (anonymised) although the app ties analytics to the fan's account with `identify(user.id)` after sign-in. Saving the ticket name and signing out happen on one tap, and saving the name also rewrites the face of every ticket the fan already holds (`components/entity/user/update-personal-details` "Correction"). Finally, the only way into Settings is a gear at the top-right of the page header, out of thumb reach; the FAB launcher exists precisely to move such controls out of that zone.

## What Changes

- **Order.** Signed-in fans see: Account → Name on your tickets → Notifications and sound → Display and controls → Help improve the service → About → Sign out → Delete account. Guests keep the sign-in hero at the top and see the same order without the account-bound sections.
- **Ticket name.** The inline form becomes one row showing the saved name and phone number; tapping it opens a bottom sheet with the form. Saving asks for confirmation and says that the tickets the fan holds will show the new name.
- **Sign out** asks for confirmation before it signs the fan out.
- **One confirmation dialog** for the screen: the withdrawal screen's modal confirmation becomes a shared component that Settings also uses (Cancel takes initial focus).
- **Privacy Policy** is a row only under About. The consent section keeps one sentence under its card with an inline link to the policy, replacing the per-toggle "privacy-policy anchor" rule.
- **Consent wording.** The section becomes 「サービス改善の協力」 with a short introduction; the toggles become 「利用状況を共有する」 and 「画面操作ログを共有する」 with descriptions that say what is collected and what it is used for, and no longer claim anonymity. The stale scenario that binds the second toggle to `marketingMeasurement` is replaced.
- **Identity verification wording.** The dedupe strength labels (「強い重複排除」「弱い重複排除」) become plain words.
- **Contact.** About gains a contact row that opens the support email address.
- **Distinct icons.** No two rows on the page share an icon.
- **Settings entry moves to the FAB.** On the four tab pages the FAB always ends with a Settings item, so the FAB now also shows on Tickets (with Settings as its only item). **BREAKING (UI):** the page header no longer shows the Settings gear. While My Artists is in edit mode the FAB stays hidden, as today.

Out of scope: whether an identity-verified fan may still change the ticket name (a separate issue, to be decided with `identity-ekyc-jpki`); the guest hero; push subscription logic; the withdrawal flow itself; the PocketSign flow; the text of the Privacy Policy.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `components/infrastructure/fan/web/route/settings`: section order; consent section name, wording and single policy link; About gains a contact row and is the only Privacy Policy row; ticket name edited in a sheet with a confirmation; Sign out confirmed; the account section is no longer "bottom"; the first visible row on load; plain identity-verification strength labels; distinct row icons.
- `components/infrastructure/fan/web/global/fab-menu`: the launcher ends with a Settings item on the four tab pages, so it shows on Tickets; a route can hide the launcher (My Artists edit mode).
- `components/infrastructure/fan/web/global/page-header`: the Settings gear requirement is removed.
- `components/infrastructure/fan/web/global/bottom-nav-bar`: Tickets now shows the FAB and its notch; the "no notch" example moves to a route outside the tabs.
- `components/infrastructure/fan/web/route/my-artists`: edit mode hides the launcher instead of only contributing no actions.

`components/infrastructure/fan/web/route/delete-account` keeps its behaviour (a modal confirmation whose Cancel takes initial focus); only its implementation moves to the shared component.

## Impact

- Frontend only: `src/routes/settings/` (template, view model, CSS, unit spec), a new `src/components/confirm-dialog/` (with stories), `src/routes/delete-account/`, `src/services/fab-menu-service.ts`, `src/app-shell.ts` / `.html`, `src/components/page-header/` (gear removed, stories updated), `src/routes/my-artists/my-artists-route.ts`, `src/locales/{ja,en}/translation.json`, and the e2e tests that open Settings through the gear.
- No proto, backend or infrastructure change. Verification: unit tests, Storybook, Playwright functional e2e, and a read-only check on production after deploy.
- Overlaps `polish-fan-web-ui` (in progress), which also modifies `global/fab-menu` ("Per-route contextual action registration": Discovery's filter item) and `route/my-artists` (the hype header). The requirements touched here are different ones; whichever archives second must rebase its delta on the other.
