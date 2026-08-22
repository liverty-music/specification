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
  the operator's tenant org is resolved by **org-pinned entry** (an `org_id`
  in the URL or a remembered `org_id` → the `org:id` scope), NOT email domain
  (no fixed org id at build time, no org picker).
- Add **`login_hint` URL parameter support**: the console reads the
  `login_hint` query parameter on entry and passes it to the OIDC
  authorization request so Zitadel pre-fills the operator's email. Combined
  with `org_id`, this is the first-time sign-in mechanism: the provisioning
  backend sends one invitation email with a link of the form
  `organizer.{base}/?org_id=<id>&login_hint=<email>`; for uninitialized
  operators Zitadel's login v2 then handles passkey registration within the
  OIDC auth-request context and redirects to the console on completion.
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
  shared client with org-pinned entry + `login_hint` support, role-claim route
  guard, placeholder; a CI assertion that the consumer chunk graph contains no
  organizer module.
- **cloud-provisioning**: the `organizer.{base}` host (HTTPRoute, cert, Cloud
  DNS) + per-host ConfigMap; mirrors `admin-console-hosting`. No proto changes.
- **backend (organizer-accounts provisioner)**: (a) replace
  `CreatePasskeyRegistrationLink` with `CreateInviteCode(SendInviteCode)` whose
  `url_template` points at the console
  (`organizer.{base}/?org_id=<id>&login_hint=<email>`, code omitted). Zitadel's
  own SMTP sends the branded invitation email — the backend has no direct
  email/SMTP infrastructure. See design D5. (b) **v1.39.0 fix (D6):** set the
  tenant login policy's `allow_username_password=true` (it gates the loginname
  username form + all local/passkey auth, not just passwords) and converge
  existing orgs via `UpdateCustomLoginPolicy`; `false` left invited operators on
  an empty login card.
- **frontend (v1.57.5 fix, D7):** `AuthCallbackRoute` self-heals a cross-context
  `No matching state found in storage` (duplicate-invite / multi-context) by
  restarting the OIDC flow once (one-shot guard).
