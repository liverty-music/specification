## Context

The main specs already carry the new names: the commit before this change moved the fan web specs (`route/dashboard` → `route/timetable`, `route/event` → `route/concert`, `global/live-highway` → `global/timetable-grid`, and the rest listed in its message) and renamed the terms in their text. Behaviour did not change in that commit. This change makes the URLs, the visible titles and labels, the backend's links and the frontend code match those names.

Facts the approach depends on:

- The router (`@aurelia/router` 2.0.0-rc.2) takes each route's `title` from `app-shell.ts`, written in English by hand, while the page header shows `data.titleKey` through i18n. A screen therefore has two titles today (header "Buy tickets", browser tab "Checkout"). `RouterConfiguration.customize` accepts `buildTitle(transition)`, which can build the tab title from the same i18n key.
- The first-party concert page (`routes/event`) and the timetable's sheet both read a Concert (`IConcertRpcClient.get` in `event-route.ts:157`, `Concert as LiveEvent` in `live-event.ts`); they differ only in whether the Series is first-party.
- The backend builds fan web addresses in `internal/entity/notification_message.go` (`link`), `internal/adapter/linkpreview/tags.go` (`og:url`), `internal/adapter/linkpreview/handler.go` (`GET /link-preview/events/{id}`) and `internal/infrastructure/mail/passkey_change.go` (`/passkey-recovery`). The fan web's `Caddyfile` asks for link preview tags only for paths that start with `/events/`.
- The callback addresses (`/auth/callback`, `/auth/passkeys-callback`, `/verify/callback`) are registered with Zitadel (cloud-provisioning `src/zitadel/components/frontend.ts`, `admin-console.ts`) and PocketSign (`POCKET_SIGN_CALLBACK_URL` in the fan-api configmaps). They keep their addresses.
- No LotteryEntry RPC reads one entry by id; the lottery status screen lists the fan's entries in a sale (`LotteryEntryService.ListByTicketSale`). Its address is therefore the sale's list under the concert, not `/lottery-entries/:id`.
- Tests name specs by path (`@spec components/infrastructure/fan/web/route/dashboard "<scenario>"`, `const ENTRY_SPEC = '.../route/resale-entry'`): 39 frontend files. Several backend test annotations name scenarios the rename commit reworded ("Guest opens a concert page").

## Goals / Non-Goals

**Goals:**
- A name found in one layer (spec path, file, class, element, i18n key, URL, title, analytics value) finds the same thing in every other.
- The frontend can check its route table against the spec names and addresses without network access.

**Non-Goals:**
- Splitting specs that describe more than one screen, or writing specs for screens that have none (about, consent, order, passkeys, lottery-entries, the callbacks, not-found). The constant in D2 lists them with no spec.
- Renaming backend usecases, entities or RPCs. `UserUseCase.SendPasskeyRecoveryLink` names the process, not the screen.
- Redirects from the old addresses.

## Decisions

### D1. One name per screen and part, derived from the spec path

| spec | file / class / element | i18n namespace |
|---|---|---|
| `route/<name>` | `src/routes/<name>/<name>-route.ts`, `<Name>Route`, `<name>-route` | `<name>` (camelCase) |
| `global/<name>` | `src/components/<name>/<name>.ts`, `<Name>`, `<name>` | `<name>` (camelCase) |
| a part with no spec | named for what it shows, inside the folder of the spec that owns it | inside the owner's namespace or its own |

The frontend renames that follow (folder → folder; class names follow the folder):

| now | after |
|---|---|
| `routes/dashboard` | `routes/timetable` |
| `routes/event/event-route.ts` (`EventRoute`) | `routes/concert/concert-route.ts` (`ConcertRoute`) |
| `routes/event/event-page.ts` (types `EventPageEvent`, `EventPerformer`) | `routes/concert/concert-page.ts` (`ConcertPageConcert`, `ConcertPerformer`) |
| `routes/lottery-entry` | `routes/new-lottery-entry` |
| `routes/lottery-entry-status` | `routes/lottery-entries` |
| `routes/resale-entry` | `routes/new-resale-entry` |
| `routes/passkey-recovery` | `routes/sign-in-help` |
| `routes/auth-callback` | `routes/sign-in-callback` |
| `routes/verify-callback` | `routes/identity-verification-callback` |
| `routes/tickets/wallet-view.ts` (`WalletTicket`) | `routes/tickets/ticket-view.ts` (`TicketView`) |
| `components/live-highway` (`<concert-highway>`) | `components/timetable-grid` (`<timetable-grid>`) |
| `live-highway/event-card.ts` | `timetable-grid/concert-card.ts` |
| `live-highway/event-detail-sheet.ts`, `event-sheet-hero.ts`, `event-sheet-hint.ts`, `event-follow-cta.ts`, `event-detail-utils.ts` | `components/concert-sheet/` (`concert-sheet.ts`, `concert-sheet-hero.ts`, `concert-sheet-hint.ts`, `concert-follow-cta.ts`, `concert-sheet-utils.ts`) |
| `live-highway/live-event.ts` (`Concert as LiveEvent`) | removed; import `Concert` |
| `components/event-details`, `event-cover`, `event-date-tabs`, `event-performers` | `concert-details`, `concert-cover`, `concert-date-tabs`, `concert-performers` |
| `components/dna-orb` (`DnaOrbCanvas`) | `components/artist-bubbles` (`ArtistBubbles`); `orb-renderer.ts` stays inside as the discovery orb |
| `components/all-nearby` (`NearbyConcerts`, `NearbyFilterSheet`) | `components/discovery-concerts` (`DiscoveryConcerts`, `AreaFilterSheet`) |
| `components/discovery-swap-button` | `components/discovery-swap-tile` |
| `components/fab-menu` (`fab-glyph`, `fab-toggle`, `fab-action`) | `components/action-menu` (`action-menu-glyph`, `action-menu-toggle`, `action-menu-item`) |
| `components/user-home-selector` | `components/home-area-selector` |
| `services/push-offer-service.ts` | `services/notification-prompt-service.ts` |

i18n namespaces: `dashboard` → `timetable`, `nav.home` → `nav.timetable`, `eventDetail` → `concertSheet`, `eventCard` → `concertCard`, `eventPage` → `concert`, `allNearby` → `discoveryConcerts`, `pushOffer` and `notification` → `notificationPrompt`, `userHome` → `homeAreaSelector`, `lotteryEntry` → `newLotteryEntry`, `lotteryEntryStatus` → `lotteryEntries`, `resaleEntry` → `newResaleEntry`, `passkeyRecovery` → `signInHelp`, `authCallback` → `signInCallback`, `verifyCallback` → `identityVerificationCallback`, `fabMenu` → `actionMenu`. Screen titles move to `nav.<name>` (design D3), and the localized `<name>.title` keys (`checkout.title`, `lotteryEntry.title`, `passkeyRecovery.title`, `verifyEmail.title`, `notifications.title`, `passkeys.title`, `deleteAccount.title`, …) go away.

Alternative: rename only the folders and leave i18n keys. Rejected: the keys are what a translator and a grep meet first, and a half rename is the inconsistency this change removes.

### D2. A constant of route spec names and addresses, checked by a unit test

`src/route-specs.ts` lists every routed fan screen: its spec name (`'timetable'`, or `null` for a screen with no spec) and its address pattern, copied from the requirement of that spec that states the address ("The screen's address" in most route specs; the address requirements already in route/discovery, route/notifications, route/legal and route/sign-in-help):

```ts
export const ROUTE_SPECS = {
  timetable: { spec: 'route/timetable', path: 'timetable' },
  concert: { spec: 'route/concert', path: 'concerts/:id' },
  'lottery-entries': { spec: null, path: 'concerts/:id/lottery-entries' },
  // …
} as const
```

The route table in `app-shell.ts` takes each `path` from this constant. `src/route-specs.spec.ts` checks, for every non-redirect route: the component's import path is `./routes/<name>/<name>-route`, the module exports `<Name>Route`, `data.titleKey` is `nav.<name>` (camelCase), and the path equals the constant's. The constant is a second copy of what the specs state; a spec change that moves an address also changes this file (a task line in every such change).

Alternative: clone the specification repository in frontend CI and compare against the spec files. Rejected by the user: the clone costs every CI run for a check a constant already gives.

### D3. One English title per screen, from one i18n key

The project already keeps invariant English expressions in one registry (`global/i18n` "Brand Expression Registry", Layer B) and binds a tab page's header to its `nav.*` label (the same requirement's scenario "Navigation tab labels are invariant across locales", and route/settings "Settings Page Header Label"). This change extends that rule to every screen instead of adding a second key: each screen's title is a registry row bound as `nav.<name>`, with the same English value in `en` and `ja`. The page header shows it, and `buildTitle` builds the browser tab title from the same key through `I18N`, so the hand-written `title:` strings in `app-shell.ts` go away. A route whose screen has no page header still sets `data.titleKey`; a flag (`data.header: false`) keeps the header hidden on the screens page-header "Routes without a page header" lists.

Alternative: a new `<name>.title` key per screen. Rejected: it duplicates `nav.<name>` for the tab screens and contradicts the registry rule above.

Other visible copy that names a screen follows the same words: the Discovery swap tile reads 「ライブ」 / "Concerts" (was 「近くのライブ」 / "Near you"), the timetable's empty-state link reads 「ライブを探す」, and the page-help section of Discovery is titled 「ライブ」 / "Concerts".

### D4. Addresses

The address table is in proposal.md. Details:

- The timetable keeps one route with path `timetable`; `concert` is a query parameter like the filters, so opening the sheet writes `?concert=<id>` next to `artists`/`journey`/`from` with `history.pushState`, and closing removes it with `replaceState`. The `concerts/:id` second path of the timetable route goes away.
- `concerts/:id` is the first-party concert page; `concerts/:id/checkout`, `concerts/:id/lottery-entries/new`, `concerts/:id/lottery-entries` and `concerts/:id/resale-entries/new` are its children. Seat type and sale go in the query (`stock`, `sale`), so nesting stays one level deep.
- Discovery's view query becomes `view=concerts` (was `view=nearby`); the device-kept value of `discovery.view` becomes `'concerts'`, and an old `'nearby'` value reads as the default Artists view. `discovery.nearbyFilter` becomes `discovery.concertsFilter`; the old key is removed on startup like `push.offerDeclines`.
- `/passkey-recovery` becomes `/sign-in-help`; the backend's passkey-change email links there.
- The organizer console builds a published date's fan address in `organizer/model/concert-model.ts` (`fanPageUrlOf`) and its guide shows the address pattern in `organizer/guide/guide.html:470`; both become `/concerts/<id>`.
- Backend: `Notification.link` returns `/concerts/<id>` for a first-party concert and `/timetable?concert=<id>` otherwise; link preview serves `GET /link-preview/concerts/{id}` and sets `og:url` to `/concerts/<id>`; the Caddyfile asks for tags when the path starts with `/concerts/`.

Sources for the address rule: the Rails Routing Guide (`GET /photos/new` "return an HTML form for creating a new photo"; "only nest resources 1 level deep"; shallow nesting) and Google Search Central "URL structure" (hyphens, simple descriptive words). The SPA routers' own docs (Aurelia 2, Angular, Vue Router, React Router, Next.js, SvelteKit) state no path naming convention; Aurelia (`route-parameters.md`), Angular (`read-route-state.md`) and SvelteKit (`50-state-management.md`) put filters and similar state in the query string, which D4 follows.

### D5. Analytics values

| property | now | after |
|---|---|---|
| `EventSource` | `dashboard`, `discovery_orb`, `all_nearby` | `timetable`, `discovery_artists`, `discovery_concerts` |
| `AuthStartSource` | `dashboard_prompt`, `all_nearby_prompt`, `event_page` | `timetable_prompt`, `discovery_concerts_prompt`, `concert_page` |
| route `data.section` | `dashboard` | `timetable` |

Insights defined in cloud-provisioning (`src/posthog/components/product-analytics.ts`) filter on none of these values. Insights made by hand in PostHog are not known; tasks list them read-only and, when one filters on an old value, move it into the Pulumi program with the new value (cloud-provisioning AGENTS.md "Changing Pulumi code").

### D6. Test annotations

Tests that name a moved spec or a reworded scenario are updated in the same PR as the code they test: the 39 frontend files with old spec paths, and backend tests whose `@spec` scenario names the rename commit reworded (event page → concert page). `scripts/check-scenario-coverage.py <change> --repos <worktree>` shows the scenarios of this change without a test.

## Risks / Trade-offs

- [Two specs-to-code copies of addresses (spec text and `ROUTE_SPECS`)] → A spec change that moves an address carries a task to change `ROUTE_SPECS`; the unit test then catches a route table that did not follow.
- [Old links stop working: push notifications already delivered, emails already sent, shared `/events/<id>` posts] → Accepted: the product has no users yet. The organizer console and the fan web deploy from the same frontend PR, so the console never shows an address the fan web does not serve; links organizers already posted are re-shared after the deploy.
- [Link preview between the frontend and the backend deploy] → The frontend asks `/link-preview/concerts/<id>` before the backend serves it; the Caddyfile's not-OK branch serves the site-wide preview until the backend deploys.
- [A large rename conflicts with open frontend branches] → Merge the open PRs (#985, #889) first; do the rename in one PR per repository, folders first with `git mv` so history follows.

## Migration Plan

1. specification: merge this plan (the rename commit and the change).
2. frontend: one PR with the renames, the new routes, `ROUTE_SPECS` and the title change; deploy.
3. backend: one PR with the new links, the link preview route and the email link; deploy. Until then, a new notification links to an address the frontend no longer has, which opens not-found; no fan is affected.
4. Rollback: revert the frontend PR (and the backend PR if deployed). The specs stay renamed; only addresses roll back.
