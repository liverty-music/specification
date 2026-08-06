## 1. Backend — remove blockchain code & dependencies

- [x] 1.1 Delete `contracts/` (Foundry project, `TicketSBT.sol`, interfaces, tests, deploy script, faucet tool, `.gas-snapshot`, `slither.config.json`, `foundry.toml`)
- [x] 1.2 Delete `configs/zkp/` (verification key + testdata)
- [x] 1.3 Delete `internal/infrastructure/blockchain/` (safe + ticketsbt), `internal/infrastructure/zkp/`, `internal/infrastructure/merkle/`
- [x] 1.4 Delete entry/ticket-mint/merkle/nullifier entities (`internal/entity/entry.go`, `merkle.go`, `safe_predictor.go`, `ticket.go`, `zkp_signals.go`) and their tests + mocks
- [x] 1.5 Delete ticket/entry repositories (`internal/infrastructure/database/rdb/{ticket,merkle,nullifier}_repo.go`) and tests
- [x] 1.6 Delete ticket/entry use cases (`internal/usecase/{ticket_uc,ticket_mint_uc,entry_uc,entry_integration}*`) and mocks
- [x] 1.7 Delete ticket/entry RPC handlers + mappers (`internal/adapter/rpc/{entry_handler,ticket_handler,mapper/ticket}*`)
- [x] 1.8 Remove ticket/entry provider wiring from `internal/di/provider.go`
- [x] 1.9 Remove `gnark`, `vocdoni/circom2gnark`, `go-ethereum`, `gnark-crypto`, `icicle-gnark` from `go.mod`; run `go mod tidy`
- [x] 1.10 Run backend `make check`; confirm build + lint + tests green with blockchain code gone

## 2. Backend — database migration

- [x] 2.1 Confirm whether the five `20260221…`–`20260223…` ticket migrations were applied in prod (not just dev)
- [x] 2.2 Author forward migration: `DROP TABLE nullifiers, merkle_tree, tickets`; `ALTER TABLE users DROP COLUMN safe_address`; `ALTER TABLE events DROP COLUMN merkle_root` (Atlas format)
- [x] 2.3 Run `atlas migrate hash`; verify apply on local PostgreSQL; author the DOWN migration
- [x] 2.4 Confirm no preserved reader (`ticket-journey`, `ticket-email-import`) references the dropped tables/columns

## 3. Backend — messaging & analytics

- [x] 3.1 Remove the `ticket.mint.completed` and `entry.zk_proof.verified` emitters from the analytics code
- [x] 3.2 Remove the `ENTRY` stream and the `TICKET` stream (mint subject) from `messaging/streams.go`; keep `TICKET_JOURNEY` and `TICKET_EMAIL`
- [x] 3.3 Remove any KEDA scaledobject triggers for the retired entry/ticket subjects in `cloud-provisioning`
- [x] 3.4 Move `ticket.mint.completed` + `entry.zk_proof.verified` to the Removed events section of the analytics catalogue doc

## 4. Backend — CI

- [x] 4.1 Remove the `slither`, `forge-test`, and gas-snapshot CI jobs (they reference the deleted `contracts/`)
- [x] 4.2 Confirm remaining backend CI (`go test ./...` + `golangci-lint`) passes without contract paths

## 5. Frontend — remove ZKP/ticket code

- [x] 5.1 Delete `circuits/`, `prover/`, `public/circuits/`, `dist/circuits/` artifacts
- [x] 5.2 Delete `src/routes/tickets/` (route, html, css, tests)
- [x] 5.3 Delete `src/services/proof-service.ts`, `src/workers/proof.worker.ts`, `src/services/ticket-store.ts`
- [x] 5.4 Delete `src/adapter/rpc/client/{entry-client,ticket-client}.ts`, `mapper/ticket-mapper.ts`, `src/entities/{entry,ticket}.ts` and tests
- [x] 5.5 Remove PWA circuit-precache handling from `sw.ts`; lower `maximumFileSizeToCacheInBytes` back to default
- [x] 5.6 Delete `e2e/pwa/pwa-circuit-precache.spec.ts` and the tickets-route E2E/visual specs; refresh visual baselines
- [x] 5.7 Remove `Ticket.listTickets` from the store-cache primitive scope; remove any tickets nav flag/entry
- [x] 5.8 Run frontend `make check`; confirm build + tests + lint green

## 6. Specification — proto / BSR

- [x] 6.1 Remove `rpc/ticket/v1/ticket_service.proto` and `rpc/entry/v1/entry_service.proto`
- [x] 6.2 Remove blockchain-only fields/messages from entity protos (e.g., merkle root on event, ticket SBT fields) while preserving `ticket_journey` / `ticket_email` entities
- [ ] 6.3 Run `buf lint` and `buf format -w`; open PR with the `buf skip breaking` label
- [ ] 6.4 Merge PR; create GitHub Release (tag) → confirm `buf-release.yml` pushes to BSR
- [ ] 6.5 Monitor BSR gen completion via `gh run watch`

## 7. Downstream dependency bump

- [ ] 7.1 Backend: bump `buf.build/gen/go/liverty-music/schema` to the post-removal version; `go mod tidy`; `make check`
- [ ] 7.2 Frontend: bump `@buf/liverty-music_schema.*` to the post-removal version; `make check`

## 8. Cloud provisioning — secrets

- [ ] 8.1 Remove contract deployer key, Base Sepolia RPC URL, and Bundler API key from Pulumi Secret Manager
- [ ] 8.2 Remove the corresponding ExternalSecret mappings from k8s manifests
- [ ] 8.3 `pulumi preview` → get approval → apply to dev; drop the recorded Base Sepolia contract address

## 9. Ship to prod & finalize

- [ ] 9.1 Open backend PR (after BSR gen + dep bump), pass CI, merge
- [ ] 9.2 Open frontend PR (after BSR gen + dep bump), pass CI, merge
- [ ] 9.3 Release backend → prod pin bump → verify migration applied and pods healthy (ArgoCD Synced/Healthy)
- [ ] 9.4 Release frontend → prod pin bump → verify ArgoCD Synced/Healthy
- [ ] 9.5 Verify preserved features (`ticket-journey`, `ticket-email-import`) still work in prod
- [ ] 9.6 Annotate `implement-ticket-system-mvp` and `sbt-formal-verification` as superseded by this change
- [ ] 9.7 Archive `remove-blockchain-ticket-system` once all PRs are merged and shipped
