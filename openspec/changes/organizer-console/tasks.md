## 1. Frontend

- [ ] 1.1 `organizer.html` Vite/Rollup entry, bundle-isolated (separate chunk graph); reuse shared auth-service + config loader
- [ ] 1.2 OIDC via the shared `organizer-console` client with email domain discovery (no fixed org id); post-login welcome placeholder
- [ ] 1.3 Route guard: inspect the `organizer-console` project roles claim, admit only `master`, redirect unauthenticated to sign-in
- [ ] 1.4 Organizer `/config.json` loader shape (issuer + `organizer-console` client id + `api.organizer` base; no fixed org id)
- [ ] 1.5 CI assertion: consumer chunk graph contains no organizer module (reuse admin-console bundle-isolation check)
- [ ] 1.6 `make check` passes

## 2. Cloud-provisioning (hosting)

- [ ] 2.1 `organizer.{base}` host: HTTPRoute on the shared gateway + TLS cert (certmap) + Cloud DNS record (dev + prod)
- [ ] 2.2 Per-host `/config.json` ConfigMap for the organizer entry; SW bypasses cache for `/config.json`
- [ ] 2.3 Add the `organizer.{base}` redirect URIs to the `organizer-console` OIDC app (coordinate with organizer-tenancy IaC)
- [ ] 2.4 `make lint` (kustomize render) passes; `pulumi preview` shows only intended additions

## 3. Ship to prod

- [ ] 3.1 Frontend PR merged → release → organizer.html shipped
- [ ] 3.2 Cloud-provisioning PR merged → ArgoCD synced (host, cert, DNS, config)
- [ ] 3.3 Verify in prod: `organizer.liverty-music.app` serves the console over TLS; an operator signs in via email domain discovery and (with `master`) sees the placeholder; a non-master account is denied; the consumer bundle is unaffected
