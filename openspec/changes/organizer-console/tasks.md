## 1. Frontend

- [x] 1.1 `organizer.html` Vite/Rollup entry, bundle-isolated (separate chunk graph); reuse shared auth-service + config loader
- [x] 1.2 OIDC via the shared `organizer-console` client with org-pinned entry (org handle → `org:id` scope; org code / remembered `org_id` / "email me a link"; no fixed org id, NOT domain discovery); post-login welcome placeholder
- [x] 1.3 Route guard: inspect the `organizer-console` project roles claim, admit only `owner`, redirect unauthenticated to sign-in
- [x] 1.4 Organizer `/config.json` loader shape (issuer + `organizer-console` client id + `api.organizer` base; no fixed org id)
- [x] 1.5 CI assertion: consumer chunk graph contains no organizer module (reuse admin-console bundle-isolation check)
- [x] 1.6 `make check` passes

## 2. Cloud-provisioning (hosting)

- [x] 2.1 `organizer.{base}` host: HTTPRoute on the shared gateway + TLS cert (certmap) + Cloud DNS record (dev + prod)
- [x] 2.2 Per-host `/config.json` ConfigMap for the organizer entry; SW bypasses cache for `/config.json`
- [x] 2.3 Add the `organizer.{base}` redirect URIs to the `organizer-console` OIDC app (coordinate with organizer-tenancy IaC)
- [x] 2.4 `make lint` (kustomize render) passes; `pulumi preview` shows only intended additions

## 3. Ship to prod

- [x] 3.1 Frontend PR merged (#528) → release v1.46.0 → organizer.html shipped (organizer-app:v1.46.0 in prod AR)
- [x] 3.2 Cloud-provisioning PR merged (#402) → ArgoCD synced (pod Running 1/1) + prod `pulumi up` (cert ACTIVE, Cloud DNS, cert-map-entry)
- [x] 3.3 Verify in prod: `organizer.liverty-music.app` serves the console over TLS ✅; SPA shell + `/config.json` (no fixed org id, `no-store`) ✅; unauthenticated visitor is redirected to Zitadel sign-in via the guard + organizer OIDC client ✅; consumer bundle unaffected (zero organizer refs, `zitadelOrgId` intact) ✅. Org-pinned entry + full passkey ceremony verified live (2026-08-21): `?org_id=387082387839779151` → Zitadel `organization=<id>` scope + Zitadel invite email → passkey registration → `/welcome` for `pannpers+org-test-7@pannpers.dev` (owner grant confirmed). Upstream `#12499` bug avoided — the bare `passkey/set` URL is not used in the confirmed flow.

## 4. Onboarding UX — login_hint + invitation email (remaining work)

- [x] 4.1 `shared/services/auth-service.ts`: add optional `loginHint` to `signIn(options?)` and pass to `signinRedirect({ login_hint })`
- [x] 4.2 `organizer/main.ts`: read `login_hint` URL param → store alongside `org_id` → pass to `signIn()` on first guard redirect
- [ ] 4.3 `organizer-accounts` backend provisioner (separate PR in backend repo), per design D5:
  - [ ] 4.3.1 remove the `CreatePasskeyRegistrationLink(SendLink)` call (the broken dead-end email)
  - [ ] 4.3.2 add `CreateInviteCode(SendInviteCode{url_template, application_name})` for the operator — `url_template = https://organizer.{base}/?org_id={{.OrgID}}`, `application_name = "Liverty Organizer"` — so Zitadel sends the "Invitation to Zitadel Login" email (via its own SMTP) with the "Accept invite" link opening the console (WITHOUT an invite the operator hits an empty Login v2 form — verified 2026-08-21). NOT a custom backend email: the backend has no direct email/Postmark infra, only email-via-Zitadel
  - [ ] 4.3.3 derive the console base URL from the issuer (`https://auth.{base}` → `https://organizer.{base}`) so the invite link is per-environment correct; no new config needed. (`login_hint` is NOT in the Zitadel-sent link — `url_template` has no email placeholder — so the operator enters email once at Login v2; the shipped frontend `login_hint` remains for re-issued links)
  - [ ] 4.3.4 keep the invite (re)send FATAL on failure (provisioning must not report success if the operator can't be onboarded)
- [x] 4.4 `make check` passes for frontend changes
- [x] 4.5 E2E verify: invitation email → console → Zitadel invite flow → passkey → `/welcome`. login_hint confirmed live in prod (v1.57.0, 2026-08-21): `?org_id=387082387839779151&login_hint=pannpers%2Borg-test-7%40pannpers.dev` → Zitadel redirect carries `loginName=<email>&submit=true&organization=<id>` — email pre-filled AND auto-submitted by Zitadel (operator skips the email entry step entirely, goes directly to passkey auth). Exceeds the spec requirement.
