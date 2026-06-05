## Context

Liverty's ticket-entry flow uses a Semaphore-style Groth16 zk-SNARK: the fan proves on-device that they know a `trapdoor` whose Poseidon commitment is a leaf in an event's Merkle tree, plus a nullifier to prevent double-entry. Proof generation runs in a Web Worker (`proof.worker.ts`) so the `trapdoor` (private input) never leaves the device — this client-side locality IS the privacy guarantee. The backend verifies with `gnark` (Apache-2.0) via the `vocdoni/circom2gnark` adapter.

**Decision history — why the GPL library is here.** The original ticket-system MVP research (`implement-ticket-system-mvp/research/zkp-browser-client.md`, 2026-02-20) selected `circom + snarkjs` on three grounds: (1) it was the only production-ready browser Groth16 prover whose output the `gnark` backend can verify; (2) full offline WASM support for venue entry; (3) the `circomlib` template ecosystem (Poseidon/Merkle/nullifier). **License was never an evaluation criterion** — `snarkjs`, `ffjavascript`, and `circomlib` are all GPL-3.0, and this was not noticed. The same research explicitly flagged `arkworks` (`ark-circom`) as the intended successor "if [browser `wasm-bindgen`] lands in 2026 … 10–20x faster proving and compatible Groth16 output," tracked via mopro issue #290. As of 2026-06 that tooling has landed (mopro documents web builds via `wasm-bindgen-rayon` with the arkworks circom prover). This change therefore executes a pre-scoped upgrade, not a novel rewrite.

**The two GPL vectors in the distributed bundle:**
1. Proving runtime: `snarkjs` + `ffjavascript` (GPL-3.0), imported verbatim into the worker chunk.
2. Circuit artifacts: `ticketcheck.wasm` (2.0 MB) + `ticketcheck.zkey` (3.1 MB), compiled from a circuit that `include`s `circomlib`'s GPL-3.0 `poseidon.circom`.

Backend verification (`gnark` / `circom2gnark`) is already permissively licensed and is not a GPL source.

## Goals / Non-Goals

**Goals:**
- Remove all copyleft (GPL-3.0) licensed code from the distributed frontend bundle, across both vectors.
- Preserve the proof's verifiability by the existing `gnark` backend (BN254 Groth16, snarkjs-compatible proof JSON), ideally with zero backend change.
- Preserve on-device proof generation (privacy), offline capability (Service Worker caching), and SHA-256 circuit-integrity verification.
- Resolve, before any irreversible swap, the two cost-determining unknowns (R1CS reuse; browser prover viability).

**Non-Goals:**
- The OSS-license page UI and the legal three-set (terms / privacy / OSS licenses) — separate change.
- Moving proof generation server-side — rejected: it would expose the `trapdoor` and destroy the zero-knowledge privacy model.
- Migrating to a non-Groth16 proof system (Noir/halo2/plonky2) — rejected: incompatible with the `gnark` Groth16 verifier (same constraint that drove the original snarkjs choice).
- Changing the `EntryService` RPC contracts (`GetMerklePath` / `VerifyEntry`) — they are library-agnostic and unchanged.

## Decisions

### Decision 1: Path A (replace with permissive prover) over Path B (arm's-length isolation) — RECOMMENDED, final call gated

**Choice (recommended):** Path A — eliminate the GPL code physically. Swap `snarkjs` → `ark-circom`/arkworks (MIT/Apache) WASM prover; swap `circomlib` poseidon → an MIT-relicensed Poseidon source and recompile.

**Rationale:** For a proprietary, app-store-bound product, removing the GPL code is unambiguous and one-time. The only hard constraint that ever justified snarkjs — gnark-verifiable Groth16 output — is met by arkworks (same BN254 Groth16). Current proof time (~2 s in-browser for this 5286-constraint circuit) is already acceptable, so Path A is justified by licensing alone; the potential 10–20x speedup is a bonus that de-risks "will a rewrite hurt mobile UX."

**Alternative — Path B (fallback):** Keep `snarkjs` but treat the Web Worker as a separate GPL-3.0 program communicating at arm's length via `postMessage` (serialized `{input}` → `{proof}`, no linking/shared memory ≈ mere aggregation). Ship the worker chunk as the GPL component with a written source offer + license text. Near-zero code change, but relies on the contested separate-program interpretation and on the bundler never inlining `snarkjs` into the main chunk. Reserve as an interim if a launch deadline precedes Path A completion, or if a verification gate makes Path A infeasible.

**The final A/B decision is gated by the two verification tasks below — keep it open until both report.**

### Decision 2: Reuse the existing `.zkey` / verification key if the recompiled R1CS is identical

**Choice:** Use an MIT-licensed Poseidon `circom` source that is structurally identical to `circomlib`'s (e.g., the Semaphore-relicensed `poseidon.circom`, MIT since 2022-07; Poseidon's BN254 constants are spec-fixed, so a faithful reimplementation yields the same constraints). Recompile and compare the R1CS / circuit hash against the current artifacts.

- **Identical** → reuse existing `ticketcheck.zkey` and backend `verification_key.json`; no new trusted setup; backend untouched.
- **Divergent** → run a fresh Groth16 phase-2 setup and deploy a new `verification_key.json` to the backend (coordinated cross-repo change).

**Rationale:** This is the single largest cost fork. Reuse keeps the change frontend-local; divergence pulls in a ceremony + backend release.

### Decision 3: Preserve the proof-JSON / gnark contract with a thin adapter if needed

**Choice:** The new prover must emit a proof + public signals that `vocdoni/circom2gnark` → `gnark.Verify` accepts unchanged. `ark-circom` outputs Groth16/BN254 but its native serialization may differ from snarkjs's `proof.json` shape; if so, add a thin frontend adapter that re-serializes to the snarkjs format the backend already parses.

**Rationale:** Keeps backend verification a no-op change and isolates all churn to the frontend.

### Decision 4: Threading model is an open decision tied to cross-origin isolation

**Choice (deferred):** Prefer multithreaded WASM (`wasm-bindgen-rayon`) for the speedup, but only if cross-origin isolation (COOP/COEP) can be enabled without breaking the PWA (Service Worker, CSP, PostHog and other third-party embeds). Otherwise fall back to single-threaded WASM and accept slower proving. Resolved by verification gate 2.

## Risks / Trade-offs

- **R1CS divergence forces a trusted-setup + backend vkey deploy** → Mitigation: verification gate 1 compiles and diff-checks the R1CS hash before committing; if divergent, coordinate a backend `verification_key.json` release via the cross-repo workflow.
- **`ark-circom` browser path is less battle-tested than its mobile-native path** (mopro's core is iOS/Android UniFFI bindings; Liverty is PWA-first and needs the pure-browser WASM path) → Mitigation: verification gate 2 spikes the actual browser build and benchmarks on real mobile browsers before adoption.
- **Multithreaded WASM requires COOP/COEP**, which can break third-party embeds and complicate CSP → Mitigation: treat threading as optional; validate header impact in a spike; single-threaded fallback always available.
- **New Rust→WASM build step** adds toolchain complexity (`wasm-bindgen`, possibly `wasm-pack`) to a TS frontend → Mitigation: vendor a prebuilt WASM artifact + bindings, or isolate the Rust build behind a single make target; keep it out of the hot dev loop.
- **Bundle/WASM size regression** vs current snarkjs (~1–1.5 MB JS + 5.2 MB artifacts) → Mitigation: measure in gate 2; the artifacts are reused, only the prover JS/WASM changes.
- **Interim Path B legal interpretation may be rejected by counsel** → Mitigation: Path B is fallback-only and time-boxed; Path A remains the target end state.

## Migration Plan

1. Run verification gate 1 (R1CS reuse) and gate 2 (browser prover viability) — both are reversible spikes, no production impact.
2. Decide A vs B from gate results; record the decision here.
3. (Path A) Recompile circuit from MIT Poseidon; regenerate artifacts + SHA-256 integrity manifest; reuse or regenerate `.zkey`/vkey per gate 1.
4. (Path A) Integrate the arkworks WASM prover behind the existing `ProofService` interface; keep `proof.worker.ts`'s `postMessage` contract stable; add the proof-JSON adapter if needed.
5. Verify end-to-end against the unchanged (or newly-keyed) backend with a known-good proof round-trip.
6. Remove `snarkjs` / `ffjavascript` from `package.json`; confirm the distributed bundle is GPL-free.
7. **Rollback:** the prover swap is behind the worker boundary; reverting the dependency + artifacts restores the prior behavior. If a new vkey was deployed, roll it back in lockstep with the frontend.

## Open Questions

- **A vs B final decision** — pending verification gates (Decision 1).
- **R1CS identical?** — pending compile-and-diff (Decision 2 / gate 1).
- **Multithreaded vs single-threaded WASM** — pending COOP/COEP feasibility on the PWA (Decision 4 / gate 2).
- **`ark-circom` directly vs via mopro** — direct `circom-compat` + hand-rolled `wasm-bindgen` wrapper, versus mopro's adapter; decide in gate 2 by maintenance/bundle trade-off.
