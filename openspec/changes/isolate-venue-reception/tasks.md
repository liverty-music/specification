## 0. Planning follow-ups (specification)

- [ ] 0.1 In `ticket-wallet-and-checkin` (unarchived): amend `components/infrastructure/organizer/web/route/reception-links` so the link URL is on the reception origin with the token in its fragment (replacing `/reception#<token>`), state in its design that reception is hosted per this change, and mark tasks 4.6, 5.6, 7.2 and 7.3 as depending on this change being in production; verify `openspec validate ticket-wallet-and-checkin --strict` passes

## 1. Infrastructure identity and DNS (cloud-provisioning, Pulumi)

- [ ] 1.1 Add the `reception-api` GSA with Workload Identity on `ns/backend/sa/reception-api`, its Cloud SQL IAM user and the operational project roles of D3 (no storage signing, no provisioner key); verify `tsc` and `biome check` pass and the prod `pulumi preview` shows only the new resources
- [ ] 1.2 Add `reception` and `api.reception` to the service list in `src/gcp/components/network.ts` (Cloudflare records, gateway certificates); verify the prod `pulumi preview` and, after `pulumi up`, that both hostnames resolve and the certificates are ACTIVE

## 2. Backend (D1-D3)

- [ ] 2.1 Grant migration: `reception-api@%.iam` gets the reception reads and writes of D3, and `organizer-console-api@%.iam` loses the reception-only writes; register it in the Atlas kustomization; extend `migration_grants_integration_test.go` with a `receptionWrites` list and the reduced `organizerWrites`; verify the test passes with every migration applied
- [ ] 2.2 Reception server: `RECEPTION_SERVER_PORT` (8092) and `RECEPTION_CORS_ALLOWED_ORIGINS` config, `ReceptionPublicProcedures()`, the unknown-token interceptor, `ReceptionService` mounted only there and started in `cmd/api/main.go` with the other servers; verify a server test that Open and Admit succeed without a sign-in on the reception server, and that no other procedure is served there
- [ ] 2.3 Organizer server without public procedures: remove `ReceptionService` and `OrganizerPublicProcedures()` from it; verify a server test that calling ReceptionService on the organizer server fails (Unimplemented or Unauthenticated) and that the existing organizer boundary tests pass
- [ ] 2.4 Run the reception integration test (`reception_admit_integration_test.go`) with the reception path connected as a role holding only the `reception-api` grants; verify it passes
- [ ] 2.5 `make check` passes in backend

## 3. Workloads and routes (cloud-provisioning, k8s)

- [ ] 3.1 `reception-api` Deployment (image `server`, exposing only 8092, probes on 8092, 2 replicas), Service, HTTPRoute for `api.reception.*`, health check policy, ServiceAccount and per-overlay config (`DATABASE_USER=reception-api@...iam`, `RECEPTION_CORS_ALLOWED_ORIGINS`); verify `kubectl kustomize` renders the dev and prod overlays
- [ ] 3.2 `reception-web` Deployment, Service and HTTPRoute for `reception.*`, mirroring `organizer-console-web`; verify `kubectl kustomize` renders the dev and prod overlays
- [ ] 3.3 Production rollout: verify read-only that the AtlasMigration is applied, both Deployments are Available, and `api.reception` answers a health check

## 4. Frontend (D4)

- [ ] 4.1 Reception app with its own build: `vite.reception.config.ts` (input `reception.html` only, output `dist-reception/`), `reception/main.ts`, its `config.json` with the reception API base URL, and the reception route, decoder, worker, client, transport and key store moved out of `organizer/`; no OIDC client. Verify the existing reception component tests pass from their new location, a dependency-cruiser rule forbids `reception/` from importing the console, the consumer app and `shared/services/auth-service`, and a post-build check finds no OIDC client or console code in `dist-reception/` (output size reported)
- [ ] 4.2 Remove the reception route from the organizer shell and point the reception-links screen's URLs at the configured reception origin (`https://reception.<domain>/#<token>`); verify its component tests for the URL shape
- [ ] 4.3 `Dockerfile.reception` (only `dist-reception/` and its `config.json`) and `Caddyfile.reception`; the release workflow builds and publishes the `reception-web` image; verify the workflow run succeeds and the image contains no `assets/organizer/`, `assets/admin/` or consumer chunks
- [ ] 4.4 `make check` passes in frontend

## 5. Production verification

- [ ] 5.1 On production with a test event: issue a link in the console, open it on a phone at `reception.liverty-music.app`, bind, and admit a test ticket through `api.reception`; verify the admission is recorded and the console origin's storage was never loaded by the reception page (no console tokens visible in the reception origin's storage)
- [ ] 5.2 Verify read-only that a ReceptionService call to `api.organizer` is refused and that the `organizer-console-api` role has no UPDATE on `tickets.admitted_at` nor INSERT on `admissions` and `rejected_scans` (`\dp` through the read-only `db-proxy`)
