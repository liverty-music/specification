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
- [x] 4.3 `organizer-accounts` backend provisioner — SHIPPED: PR #399 (branch `organizer-invite-onboarding`) merged → backend **v1.38.0** "organizer console-pointed invite email onboarding" → **deployed to prod** 2026-08-22 (fan-api + admin-console-api on v1.38.0). Per design D5:
  - [x] 4.3.1 remove the `CreatePasskeyRegistrationLink(SendLink)` call (the broken dead-end email)
  - [x] 4.3.2 add `CreateInviteCode(SendInviteCode{url_template, application_name})` as the **email transport** — `url_template = https://organizer.{base}/?org_id=<zitadelOrgID>&login_hint=<operatorEmail>` (org id + email baked in as literals in Go; `{{.Code}}` deliberately OMITTED so no credential is in the link), `application_name = "Liverty Organizer"` — so Zitadel's SMTP sends the "Invitation to Zitadel Login" email whose "Accept invite" link opens the console. NOT a functional prerequisite: Login v2 auto-onboards a no-auth-method + verified-email operator on its own (source-verified `apps/login/src`@v4.14.0: `loginname.ts` → `/verify?invite=true&send=true` → `verify.ts` → `/authenticator/set` → `completeFlowOrGetUrl(requestId)`). Used only because the backend has no SMTP of its own. (The earlier "empty form ⇒ invite required" was a misread of a deleted-operator/no-user-found state — D5.)
  - [x] 4.3.3 derive the console base URL from the issuer (`https://auth.{base}` → `https://organizer.{base}`) so the invite link is per-environment correct; no new config needed. Bake `login_hint=<operatorEmail>` into the `url_template` (email known at provisioning) so the link pre-fills + auto-submits the loginname step — the operator never types their email (impl `510ea3d`: `%s/?org_id=%s&login_hint=%s`, both `url.QueryEscape`d)
  - [x] 4.3.4 keep the invite (re)send FATAL on failure (provisioning must not report success if the operator can't be onboarded); an already-onboarded operator's re-invite rejection is treated as benign (idempotent saga, `66b1a6a`)
- [x] 4.4 `make check` passes for frontend changes
- [x] 4.5a `login_hint` prefill verified live in prod (frontend v1.57.0, 2026-08-21): `?org_id=387082387839779151&login_hint=pannpers%2Borg-test-7%40pannpers.dev` → Zitadel redirect carries `loginName=<email>&submit=true&organization=<id>` — email pre-filled AND auto-submitted (operator skips the email-entry step). `requestId` preserved through the console→OIDC redirect.
- [x] 4.5b Full invite-onboarding E2E on the SHIPPED flow — **VERIFIED in prod 2026-08-22** (backend **v1.39.0** + frontend **v1.57.5**) with a genuinely-uninitialized operator (`org-test-21`): fresh Organizer via admin → `CreateInviteCode`-sent console-pointed invite email → "Accept invite" → console (org pinned, `login_hint` auto-submits) → OIDC → `/verify` (code) → passkey registration → `/auth/callback` → **`/welcome`** (owner-gated placeholder, operator email shown). Two latent defects were surfaced and fixed along the way — see 4.6 (login policy) and 4.7 (callback self-heal).

- [x] 4.6 **Login-policy fix (backend v1.39.0, PR #400)** — design D6. The provisioner's `allow_username_password=false` disabled the loginname username form entirely (that field gates ALL local auth incl. passkey), giving invited operators an empty login card. Set `allow_username_password=true` (passkey-primary = local-auth-ON + `PasswordlessType=ALLOWED` + no password on the operator); converge pre-existing orgs via `UpdateCustomLoginPolicy` on the AlreadyExists path. Identity-layer proof: `org-test-20`=false (broken) vs `org-test-21`=true (fixed). Shipped + prod-deployed (fan-api + admin-console-api on v1.39.0).

- [x] 4.7 **Callback self-heal (frontend v1.57.5, PR #560)** — design D7. `AuthCallbackRoute` self-heals a cross-context `No matching state found in storage` (duplicate-invite / multi-context) by restarting the OIDC flow once (one-shot `sessionStorage` guard, fails closed, clears on success); 6 unit tests. Shipped + prod-deployed (`organizer-console-web-app` v1.57.5).

- [x] 4.8 **Duplicate invitation emails (upstream Zitadel, tracking only)** — design D7 note. Backend sends exactly one `CreateInviteCode`; the hosted Login v2 `/verify?invite=true` page re-fires `CreateInviteCode` on every render, producing duplicate "Invitation to Zitadel Login" emails. Not fixable in our code; filed as tracking issue **liverty-music/specification#843**. Harmless (identical links, no code in link).
