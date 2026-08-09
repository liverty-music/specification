## Context

The blockchain ticket system (SBT minting, ERC-4337 Safe address prediction, off-chain ZKP entry) shipped across all four repos via several archived changes (`align-ticket-rpcs-with-auth-scoping`, `refactor-mint-ticket`, `remove-gpl-zk-prover`, and the SBT-CI changes) plus the still-open `implement-ticket-system-mvp` (72/79). The code is **live in `main` but dormant**: the frontend ticket-sales navigation is hidden behind a flag, and the backend handlers are wired into DI but unreachable in production because they depend on dev-only Secret Manager entries (contract key, Base Sepolia RPC, Bundler API key). A fair MVP-and-future assessment concluded the platform is a walled garden (Scenario A), so this change removes the blockchain stack cleanly rather than leaving dead code and a custodial key as standing liabilities.

This is a **cross-repo teardown** touching `specification` (proto/BSR), `backend` (Go + Foundry + migrations + JetStream), `frontend` (circuits/prover/route/PWA), and `cloud-provisioning` (Secret Manager). The ordering matters because the proto services are consumed via BSR by both backend and frontend, and because JetStream streams and an applied DB migration are involved.

## Goals / Non-Goals

**Goals:**
- Remove all blockchain-specific ticket code, dependencies, contracts, circuits, and secrets.
- Drop the blockchain DB schema (`tickets`, `merkle_tree`, `nullifiers`, `users.safe_address`, `events.merkle_root`) with a backward-compatible forward migration.
- Retire the blockchain proto services from BSR without breaking the preserved Web2 ticket services.
- Preserve the Web2 features `ticket-journey` and `ticket-email-import`, and general Passkey auth, untouched.
- Leave the codebase in a clean state for a future, separate Web2 ticket change.

**Non-Goals:**
- Designing or building the Web2 replacement (account-bound tickets + signed rotating QR). That is a separate follow-up change.
- Un-deploying the Base Sepolia `TicketSBT` contract (it is a testnet artifact; abandoning it is sufficient).
- Touching `ticket-journey` / `ticket-email-import` behavior or their JetStream streams.

## Decisions

### Decision 1: Remove consumers before the proto contract (dependency-safe ordering)

Delete the backend and frontend code that imports the generated `TicketService` / `EntryService` types **first**, land those, then remove the services from the proto schema and cut a BSR release. This avoids a window where downstream repos reference removed generated types. The proto removal is a **breaking change**, so the `specification` PR carries the `buf skip breaking` label per repo convention.

**Alternative considered**: Remove proto first — rejected; it would red-CI backend/frontend until their removals land, violating the "downstream builds stay green" rule.

### Decision 2: Forward DROP migration, not migration deletion

The five ticket migrations (`20260221…`–`20260223…`) are already applied in environments, so they are immutable history. Removal is a **new forward migration** that `DROP`s the tables and columns. Because nothing outside the removed code reads `tickets` / `merkle_tree` / `nullifiers` / `users.safe_address` / `events.merkle_root` (verified: `ticket-journey` and `ticket-email-import` do not depend on them), the drop is backward-compatible for all preserved readers. Authored in Atlas format with `atlas migrate hash`, following the hand-authored-migration pattern (local canary is known-broken).

**Alternative considered**: Leave tables dormant — rejected; the user chose clean removal, and empty orphan tables plus a `safe_address` column are avoidable schema debt.

### Decision 3: Retire ENTRY stream and the TICKET mint subject; keep TICKET_JOURNEY / TICKET_EMAIL

`messaging/streams.go` defines `ENTRY` (`ENTRY.*`), `TICKET` (`TICKET.*`, carrying `TICKET.mint_completed`), `TICKET_JOURNEY`, and `TICKET_EMAIL`. `ENTRY` is fully removable. For `TICKET`: its only subject is the blockchain `mint_completed` analytics event, so the stream is removed too — but **only after** the emitter is deleted, to avoid a subscriber binding to a subject that no longer publishes. `TICKET_JOURNEY` and `TICKET_EMAIL` are Web2 and stay. Per the stale-durable-wedge lesson, delete the obsolete durables/consumers explicitly and confirm via `nats consumer ls` after rollout; do not rely on passive cleanup.

**Alternative considered**: Keep `TICKET` stream for a future Web2 mint event — rejected; a future event will define its own subject/stream, and keeping an unused stream risks a stale-durable wedge.

### Decision 4: Remove analytics events at the spec + catalogue level

`ticket.mint.completed` and `entry.zk_proof.verified` move from `dormant` to the Removed events section of the `product-analytics` catalogue. This keeps the "no phantom events" invariant intact and documents the deletion. `ticket.email.parsed` stays (Web2, still dormant).

### Decision 5: Supersede the in-flight blockchain proposals

`implement-ticket-system-mvp` (72/79) and `sbt-formal-verification` (0/34, no code) are annotated as superseded by this change under Scenario A. Neither is archived (archive implies shipped-as-designed). `sbt-formal-verification` has no landed code, so its retirement is documentation-only.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| BSR breaking removal reddens downstream CI if ordering slips | Land backend+frontend consumer removals first; add `buf skip breaking`; release BSR; then bump downstream deps |
| Stale JetStream durable for ENTRY/TICKET wedges other consumers | Delete emitters first, then streams; explicitly delete durables; verify `nats consumer ls` + no `<unknown>` in HPA post-rollout |
| Applied-migration DROP is irreversible in prod | Confirm zero rows / zero readers before drop; ship DOWN migration; drop is backward-compatible (no preserved reader touches the objects) |
| Hidden coupling from a preserved feature to a dropped symbol | Pre-verified `ticket-journey` / `ticket-email-import` independence; `make check` in backend + frontend must pass after each repo's removal |
| `go mod tidy` surfaces an unrelated advisory (govulncheck repo-wide reddening) | If it happens, split a dedicated deps-bump PR and rebase, per the known govulncheck gate behavior |
| Removing `contracts/` also removes Slither/forge CI jobs | Remove the CI job definitions in the same PR so CI config does not reference deleted paths |
| Frontend visual/pwa baselines reference the tickets route / circuit precache | Delete the `tickets` and `pwa-circuit-precache` E2E/visual specs; refresh visual baselines per the main-branch baseline-artifact process |

## Migration Plan

1. **backend (consumers)**: delete entry/ticket/merkle/nullifier code, `contracts/`, `configs/zkp/`, `blockchain/`/`zkp/`/`merkle/` infra, DI wiring, crypto deps (`go mod tidy`); remove Slither/forge CI jobs; add the forward DROP migration (`atlas migrate hash`); retire `ENTRY` stream + `TICKET.mint_completed` emitter/stream; remove the two analytics events. `make check` green. Open PR (does not yet touch proto-generated types beyond deletion of their callers).
2. **frontend (consumers)**: delete `circuits/`, `prover/`, `public/circuits/`, `tickets` route, proof worker/service, entry/ticket clients + stores, PWA circuit precache, and the related E2E/visual specs; refresh baselines; `make check` green. Open PR.
3. **specification (contract)**: remove `TicketService`, `EntryService`, and blockchain-only entity messages from proto; `buf lint`; PR with `buf skip breaking`; merge; GitHub Release → `buf-release.yml` pushes to BSR.
4. **backend + frontend (dep bump)**: bump the generated BSR package to the post-removal version; confirm `make check` still green with the services gone; merge.
5. **cloud-provisioning**: remove the contract key / RPC URL / Bundler API key from Pulumi Secret Manager and the corresponding ExternalSecret mappings; `pulumi preview` → apply; drop the recorded Base Sepolia address.
6. **Ship to prod**: backend release → prod pin bump → confirm migration applied and pods healthy; frontend release → prod pin bump; verify ArgoCD Synced/Healthy.
7. **openspec**: annotate `implement-ticket-system-mvp` and `sbt-formal-verification` as superseded; archive this change once all PRs are merged and shipped.

**Rollback**: Each repo's removal is an independent revert of a stateless deployment. The DB DROP is the only stateful step; its DOWN migration recreates the empty tables/columns, and no data is lost because the objects hold no production data.

## Open Questions

- Confirm whether the five ticket migrations were applied to **prod** (not just dev) so the DROP migration's environment targeting is correct.
- Confirm no PostHog dashboard/funnel currently references `ticket.mint.completed` or `entry.zk_proof.verified` before removing them (spec says they are dormant, but verify live).
- Should the preserved-but-dormant `ticket.email.parsed` event and `ticket-email-import` feature also be reviewed for Scenario A relevance, or left as-is? (Out of scope here; flag for product.)
