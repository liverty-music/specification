## Why

Organizer operators need a place to sign in. This sub-change (3/4 of roadmap
step ①) adds the **organizer console frontend + its hosting** — a
bundle-isolated `organizer.html` entry authenticated against the operator's
own Zitadel tenant org (via org-pinned entry), served at a dedicated host.
Business screens land in later changes; this establishes the
access-controlled shell. Grounded in `docs/organizer-platform-design.md` and
`docs/zitadel-tenancy-model.md`, tracked by liverty-music/specification#759.
Depends on `organizer-tenancy` (the `organizer-console` OIDC app).

## What Changes

- Add a third frontend entry point **`organizer.html`** — a Vite/Rollup MPA
  bundle-isolated from the consumer SPA and the admin console (no organizer
  code in the consumer chunk graph).
- Authenticate via Zitadel OIDC using the shared `organizer-console` client;
  the operator's tenant org is resolved by **org-pinned entry** (an org
  handle — org code/slug, remembered `org_id`, or re-issued sign-in link →
  the `org:id` scope), NOT email domain (no fixed org id at build time, no
  org picker).
- Add a **route guard** that inspects the token's `organizer-console` project
  roles and admits only operators holding `owner`; unauthenticated visitors
  are sent to sign-in; authenticated operators land on a post-login welcome
  placeholder.
- Add **hosting** for the entry at `organizer.{base-domain}`
  (`organizer.dev.liverty-music.app` / `organizer.liverty-music.app`):
  HTTPRoute on the shared gateway, TLS cert (certmap), Cloud DNS record, and
  a per-host `/config.json`.
- **Runtime config**: the organizer `/config.json` carries the issuer + the
  `organizer-console` client id + `apiBaseUrl = api.organizer.{base}`, and
  deliberately **omits a fixed `zitadelOrgId`** — the org is resolved at
  login by org-pinned entry (org handle). This organizer config shape is specified in the
  `organizer-console` capability; the consumer SPA's `frontend-runtime-config`
  contract is unchanged (it governs the consumer entry only).

Explicit non-goals: business screens (event authoring etc.); the
organizer-facing API server (`organizer-rpc-server`); per-org branding; a
reception check-in PWA.

## Capabilities

### New Capabilities
- `organizer-console`: the `organizer.html` bundle-isolated entry, OIDC
  login via org-pinned entry, the role-claim route guard + placeholder, and
  the organizer runtime-config shape (no fixed org id).
- `organizer-console-hosting`: the `organizer.{base}` host — HTTPRoute, TLS
  cert, Cloud DNS, and per-host `/config.json`.

### Modified Capabilities
<!-- None. The organizer entry defines its own config shape in the
     organizer-console capability; the consumer's frontend-runtime-config
     contract (which governs the consumer SPA entry) is unchanged. -->

## Impact

- **frontend**: new `organizer.html` entry (bundle-isolated), OIDC via the
  shared client with org-pinned entry, role-claim route guard, placeholder;
  a CI assertion that the consumer chunk graph contains no organizer module.
- **cloud-provisioning**: the `organizer.{base}` host (HTTPRoute, cert, Cloud
  DNS) + per-host ConfigMap; mirrors `admin-console-hosting`. No proto
  changes.
