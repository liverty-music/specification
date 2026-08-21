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
- [x] 3.3 Verify in prod: `organizer.liverty-music.app` serves the console over TLS ✅; SPA shell + `/config.json` (no fixed org id, `no-store`) ✅; unauthenticated visitor is redirected to Zitadel sign-in via the guard + organizer OIDC client ✅; consumer bundle unaffected (zero organizer refs, `zitadelOrgId` intact) ✅. Org-pinned entry verified with a REAL tenant (`?org_id=386611844443275630` → Zitadel `…&organization=386611844443275630`, tenant passkey-primary policy, not the default admin login) now that `organizer-accounts` (2/4) has shipped real operators with `owner` grants (server-side `user_grants5 roles={owner}` on the organizer-console project). The `owner`/non-`owner` guard + org-handle logic is unit-tested; only the physical passkey ceremony (human authenticator; subject to the known upstream login-v2 passkey/set retry-500 bug) is outside automated scope.
