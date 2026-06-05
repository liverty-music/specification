## 1. Verification Gate 1 — R1CS reuse (decides backend impact)

- [x] 1.1 Identify a permissively-licensed (MIT) Poseidon `circom` source structurally equivalent to `circomlib`'s (e.g. the Semaphore-relicensed `poseidon.circom`); record its license provenance
- [x] 1.2 Recompile `ticketcheck.circom` with the MIT Poseidon include; capture the resulting R1CS and circuit hash
- [x] 1.3 Diff the recompiled R1CS / circuit hash against the current `ticketcheck-v1` artifacts
- [x] 1.4 Record the outcome: identical → reuse existing `.zkey` + backend `verification_key.json`; divergent → schedule a fresh phase-2 trusted setup + backend vkey deploy

### Gate 1 Findings (2026-06-05) — RESULT: IDENTICAL → reuse existing `.zkey` + backend `verification_key.json`

- **Tooling**: `circom 2.1.9` (installed). Baseline = `ticketcheck.circom` compiled against `circomlib@2.0.5` (GPL-3.0) Poseidon.
- **License swap is provably R1CS-neutral.** Compiling with a structurally-identical Poseidon (same `poseidon.circom` template + `poseidon_constants.circom` constants under an MIT header) produced a **byte-identical R1CS**: `sha256(R1CS) = a8a5a293b869522b47b78fc4043007007945a5d26732379ae1e5fe6c2ba846f2` for both baseline and the relicensed copy. The license header does not affect the constraint system.
- **Committed artifact matches the fresh compile.** Parsing the committed `public/circuits/ticketcheck-v1/ticketcheck.zkey` header: `protocol=groth16, nVars(wires)=5336, nPublic=3, domainSize=8192`. The fresh compile yields wires=5336, public=3, non-linear constraints=5313 (8192 = next 2^13 ≥ 5313) — an exact match. The "5286" figure in `design.md` was approximate/stale; the real artifact is consistent with `circom 2.1.9`.
- **Conclusion**: existing `.zkey` and backend `verification_key.json` are **reusable** — no fresh phase-2 trusted setup, no backend code/vkey change — **conditional on** the chosen MIT Poseidon source being structurally identical (same constants + template) to `circomlib`'s. Final confirmation (byte-identical R1CS + identical Poseidon hash outputs) must be re-run against the *actual* vetted MIT source file once 1.1 selects it.
- **Residual (1.1, open)**: obtain and record provenance for the specific MIT Poseidon `circom` file to vendor (design names the Semaphore-relicensed copy). This is a sourcing + license-provenance decision (legal-review-worthy, since the whole change is license compliance), not a computation. `@zk-kit/circuits` was checked and is **not** a clean source — its `poseidon-proof.circom` re-`include`s `circomlib`'s GPL `poseidon.circom` and depends on `circomlib@^2.0.5`.

## 2. Verification Gate 2 — browser prover viability (decides Path A feasibility & threading)

- [x] 2.1 (a) Spike `ark-circom`/arkworks circom Groth16 proving in a pure-browser WASM build (no native bindings), reusing the existing `ticketcheck.wasm` witness calculator and `.zkey`; confirm it produces a proof in a Web Worker for a known input
- [ ] 2.2 (b) Evaluate the threading model: attempt multithreaded `wasm-bindgen-rayon` and verify whether COOP/COEP cross-origin isolation can be enabled without breaking Service Worker registration, CSP, or third-party embeds (PostHog etc.); also benchmark the single-threaded fallback
- [ ] 2.3 (c) Measure prover JS + WASM bundle size and real proof-generation time on representative mobile browsers (mid- and low-end); A/B against the current snarkjs baseline (~2 s in-browser)
- [x] 2.4 (d) Confirm the prover's proof + public-signals output is accepted by `vocdoni/circom2gnark` → `gnark.Verify`; if the native serialization differs, prototype the thin snarkjs-format JSON adapter
- [x] 2.5 Decide `ark-circom` directly (hand-rolled `wasm-bindgen` wrapper) vs via mopro adapter, based on maintenance/bundle trade-off
- [x] 2.6 Record gate 2 outcome (viable / not viable; threaded / single-threaded)

### Gate 2 Findings (2026-06-05) — RESULT: VIABLE (backend-compatible; single-threaded path sufficient). Final browser-run + mobile timing + threading deferred to implementation.

Spike crate: `ark-circom 0.6.0` (crates.io) on the arkworks **0.6** release set (ark-bn254/ark-groth16/ark-relations 0.6 — the gr1cs generation). Native prover reuses the **existing committed `ticketcheck.wasm` + `ticketcheck.zkey` unchanged** (via `ark_circom::read_zkey`).

- **2.4 — gnark accepts the arkworks proof, ZERO backend change (decisive).** Generated a Groth16 proof with `Groth16::<Bn254, CircomReduction>::prove` (the `CircomReduction` QAP is mandatory — the default `LibsnarkReduction` yields a proof the snarkjs vkey rejects), serialized to snarkjs `proof.json`, and verified it through the backend's **exact** path (`parser.UnmarshalCircomProofJSON` → `ConvertCircomToGnark` → `parser.VerifyProof`, mirroring `internal/infrastructure/zkp/verifier.go`) against the **existing committed `verification_key.json`** → `gnark VerifyProof: true`. Negative control (tampered public signal) → `pairing doesn't match`, confirming a real check. arkworks public signals match snarkjs exactly: `[merkleRoot, eventId, nullifierHash]`.
  - **Serialization adapter (5.3) is trivial**: emit field elements as decimal strings; G1 = `[x, y, "1"]`; **G2 = `[[x.c0, x.c1], [y.c0, y.c1], ["1","0"]]`** (limb order `[c0, c1]`, NOT swapped — the swapped variant fails the BN254 G2 subgroup check). No backend re-key, no proof-format change.
- **2.1 — native pipeline proven; browser path architecturally confirmed (not yet run in a Worker).** ark-circom 0.6 ships explicit `wasm32` support: `[target.'cfg(target_arch="wasm32")'.dependencies.wasmer] features=["js-default"]` — on wasm32 it executes the circom witness `.wasm` via the **browser's own WebAssembly engine** (no native VM), which is the intended PWA flow (upstream PR #89). Remaining: a `wasm-bindgen` cdylib wrapper + `getrandom` `js` feature + a headless-browser Web Worker run. Not a viability blocker; deferred to implementation (section 5).
- **2.3 — perf proxy**: native release proof ≈ **1.63 s** wall (process start + witness calc + prove), ~108 MB peak RSS. Same order as the snarkjs ~2 s in-browser baseline; single-threaded WASM will be slower but acceptable. Real mid/low-end **mobile** timing still required at implementation time (no devices in spike env).
- **2.5 — decision: `ark-circom` directly + a hand-rolled `wasm-bindgen` wrapper.** mopro wraps ark-circom but targets iOS/Android UniFFI; for a PWA-only target the direct path is leaner (smaller bundle, fewer layers) and is already proven end-to-end here.
- **2.2 — threading: DEFERRED** (needs the live PWA to test COOP/COEP vs Service Worker/CSP/PostHog). Given the single-threaded proof time is acceptable, **start single-threaded** (no COOP/COEP, section 6 skipped) and treat `wasm-bindgen-rayon` as a later optimization.

**Gate 2 verdict: Path A is viable.** Backend stays untouched (consistent with Gate 1 reuse); arkworks proof is gnark-verifiable with the existing key; browser execution is upstream-supported; single-threaded perf is acceptable.

## 3. Decision Checkpoint — Path A vs Path B

- [x] 3.1 From gates 1 & 2, decide Path A (replace) or Path B (arm's-length interim); update `design.md` Open Questions with the resolution and rationale → **Path A** (both gates passed; design.md Open Questions updated)
- [x] 3.2 If Path B is chosen as interim, branch to section 8; otherwise proceed with Path A (sections 4–7) → **Path A**, proceeding to sections 4–7

## 4. Path A — Circuit artifacts (vector ②: remove GPL Poseidon)

- [x] 4.1 Commit the MIT Poseidon include change to `frontend/circuits/ticketcheck-v1/ticketcheck.circom`; remove the `circomlib` GPL dependency from the circuit's `package.json`
- [x] 4.2 Regenerate `public/circuits/ticketcheck-v1/ticketcheck.wasm` and `ticketcheck.zkey` (reuse existing `.zkey` if gate 1 was identical; otherwise run the new trusted setup)
- [x] 4.3 Regenerate the SHA-256 circuit-integrity manifest to match the new artifacts
- [x] 4.4 If the R1CS diverged, deploy the new `verification_key.json` to the backend in lockstep (cross-repo coordination) → **R1CS did NOT diverge; no backend change**

### Section 4 done (2026-06-05) — vector ② removed

- Vendored MIT `poseidon.circom` + `poseidon_constants.circom` into `frontend/circuits/ticketcheck-v1/`; rewired `ticketcheck.circom` include from `node_modules/circomlib/...` → `./poseidon.circom`. Clean-room generator/verifier under `tools/`; provenance in `POSEIDON_PROVENANCE.md`.
- Removed `circomlib` + `circomlibjs` (both GPL, build-only, unused by frontend src) from the circuit `package.json`; deleted the stale `package-lock.json`. Circuit `package.json` now MIT.
- Recompiled `public/circuits/ticketcheck-v1/ticketcheck.wasm` from MIT sources (sha256 `d37508e4…`); **reused the existing `.zkey` unchanged** (R1CS byte-identical `a8a5a29…`). Backend vkey untouched.
- Updated the integrity manifest in `src/services/proof-service.ts` (new wasm hash; zkey hash unchanged).
- **Validated**: new MIT wasm + reused zkey → snarkjs verify `true` AND backend `gnark VerifyProof: true` against the existing vkey.

## 5. Path A — Proving runtime (vector ①: remove snarkjs)

- [x] 5.1 Add the arkworks-based WASM prover (MIT/Apache) and its build step to the frontend pipeline; keep the Rust→WASM build behind a single make target

### Section 5.1 done (2026-06-05) — arkworks WASM prover BUILT and BROWSER-VERIFIED end-to-end

New crate `frontend/prover/` (`ticketcheck-prover`, MIT): a `wasm-bindgen` `prove(input_json, circuit_wasm, circuit_r1cs, proving_key)` over `ark-circom 0.6` + `ark-groth16` (`CircomReduction`). All inputs are bytes (no filesystem) — builds the witness calculator from `Module::new(bytes)` (wasmer `js-default` runs it via the browser WASM engine), parses r1cs from a `Cursor`, `read_zkey` from a `Cursor`, emits snarkjs `proof.json` (`G2 = [c0, c1]`) + public signals.

- **Browser-verified end-to-end (the deferred 2.1 run):** in headless Chrome (Playwright) the WASM prover reused the existing committed `.zkey` + the MIT-recompiled `.wasm` + the shipped `.r1cs` and produced a Groth16 proof in **~5.2 s (single-threaded, desktop)**. That **browser-generated** proof verified `gnark VerifyProof: true` through the backend's exact `circom2gnark` path against the **existing committed vkey**. Vector ① is proven GPL-free and backend-compatible.
- **Bundle size (2.3):** prover wasm **812 KB (`wasm-opt`) / ~270 KB gzipped** — smaller than snarkjs's JS runtime. New shipped artifact: `ticketcheck.r1cs` (2.4 MB; prover needs the constraint matrices — `read_zkey` 0.6 returns only the public-input index). Total cached artifacts ~7.6 MB (was 5.2 MB); compressing/​reconstructing the r1cs is a follow-up size optimization.
- **IMPORTANT finding — single-threaded is NOT free (updates Decision 4):** `ark-circom 0.6` and `ark-groth16`'s `default = ["parallel"]` hard-enable **rayon**, whose thread-pool build PANICS in single-threaded wasm (`ThreadPoolBuildError: operation not supported`). Resolved by vendoring `ark-circom` at `frontend/prover/vendor/ark-circom` with the `parallel` features stripped + `ark-groth16 default-features = false`. The alternative (multithreaded `wasm-bindgen-rayon`) needs nightly `build-std` + COOP/COEP — deferred. The single-threaded vendored-patch path is the chosen baseline.
- **Gotcha recorded:** a `#[wasm_bindgen]` param must not be named `wasm` (it shadows the glue's internal `wasm` exports object). wasm-bindgen-cli version must match the crate (0.2.100).
- [x] 5.2 Replace `groth16.fullProve` in `src/workers/proof.worker.ts` with the new prover, keeping the worker's `postMessage` request/result contract stable
- [x] 5.3 Add the snarkjs-format proof-JSON adapter in the worker / `proof-service.ts` if gate 2(d) showed a serialization mismatch → built into the prover (emits `G2 = [c0, c1]`); no separate adapter needed
- [x] 5.4 Remove the `snarkjs` module declaration from `src/resource.d.ts`
- [x] 5.5 Apply the chosen threading decision (multithreaded + COOP/COEP, or single-threaded fallback) per gate 2(b) → **single-threaded** (vendored ark-circom without rayon `parallel`); section 6 skipped

### Section 5.2–5.5 done (2026-06-05)

- `proof.worker.ts` now imports the wasm-bindgen prover (`init` + `prove`) and the `?url` wasm asset; calls `prove(JSON.stringify(input), wasmBytes, r1csBytes, zkeyBytes)`; the `{type:'success', proof, publicSignals}` result contract is unchanged.
- `proof-service.ts` fetches + SHA-256-verifies the three artifacts and transfers the bytes zero-copy to the worker (replacing the old URL-passing). Integrity manifest now covers `ticketcheck.r1cs` too.
- `resource.d.ts`: dropped the `snarkjs` module decl; added the `*.wasm?url` decl.
- `make build-prover` isolates the Rust→WASM build; `prover/pkg/` is committed as the prebuilt artifact.
- **Validated**: `tsc --noEmit` clean, `npm run build` emits `proof.worker-*.js` + `ticketcheck_prover_bg-*.wasm` (605 KB / 245 KB gz), 28 affected unit tests pass.

## 6. Path A — Cross-origin isolation (only if multithreaded) — SKIPPED (single-threaded chosen)

- [x] 6.1 Add COOP/COEP headers in the Caddyfile / hosting config; reconcile with the existing CSP → N/A (single-threaded; no SharedArrayBuffer/COOP/COEP needed — wasmer memory is non-shared)
- [x] 6.2 Verify Service Worker registration, circuit caching, and required third-party embeds still function under isolation → N/A (no isolation imposed)

## 7. Path A — Remove GPL, verify, and ship

- [x] 7.1 Remove `snarkjs` (and transitive `ffjavascript`) from `package.json`; run `make check` → removed; lockfile synced (0 refs); typecheck + build + targeted tests pass (full `make check` to run pre-PR)
- [x] 7.2 Run a dependency license audit over the production frontend deps and confirm zero GPL-family licenses in the shipped runtime → `license-checker --production`: zero GPL-family (MIT/Apache/BSD/ISC/MPL only); Rust crates in the wasm are MIT/Apache
- [x] 7.3 End-to-end test: generate a proof with the new runtime and verify it round-trips through `VerifyEntry` → browser-generated proof verifies `gnark VerifyProof: true` via the backend's exact `circom2gnark` path against the existing vkey. (Live full-app E2E vs the dev backend is blocked — dev env intentionally stopped.)
- [x] 7.4 Update the OSS-license inventory to reflect the removed GPL deps (hand-off note to the separate OSS-license-page change) → `OSS_LICENSE_HANDOFF.md`
- [~] 7.5 Open the frontend PR (and backend PR if vkey changed); merge after CI; ship to dev, then cut the production release so the GPL-free bundle reaches prod
  - [x] frontend PR opened: liverty-music/frontend#431 (issue #429). Rebased on main; **all CI green** (Lint/Test/E2E/Smoke/Visual/Security Audit/review); MERGEABLE/CLEAN. Also regenerated `src/generated/oss-licenses.json`.
  - [x] backend PR: **NOT needed** (verification key unchanged).
  - [x] merged #431 (merge commit `3ae1f39` on main; all CI green)
  - [x] shipped to prod: Release **v1.10.0** → dev AR digest promoted to prod AR → `dispatch-prod-pin` → ci-bot `64ebd9e` "pin frontend prod overlay to v1.10.0" on cloud-provisioning:main → ArgoCD auto-sync. (Dev deploy's post-deploy-smoke fails as expected — dev env intentionally stopped — but the AR image build succeeded, which is all the prod retag needs.)

## 8. Path B — Arm's-length interim (NOT TAKEN — Path A chosen at 3.2; section retained for record)

- [ ] 8.1 Configure the bundler so the `snarkjs` proving worker builds as a separate chunk and is never inlined into the main app chunk
- [ ] 8.2 Add the GPL-3.0 written source offer + full license text to the distributed app and the OSS-license surface
- [ ] 8.3 Document the arm's-length boundary as a build invariant (guard against future bundler changes that would inline snarkjs) and schedule Path A as the follow-up end state
