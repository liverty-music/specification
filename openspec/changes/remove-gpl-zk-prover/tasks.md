## 1. Verification Gate 1 — R1CS reuse (decides backend impact)

- [ ] 1.1 Identify a permissively-licensed (MIT) Poseidon `circom` source structurally equivalent to `circomlib`'s (e.g. the Semaphore-relicensed `poseidon.circom`); record its license provenance
- [ ] 1.2 Recompile `ticketcheck.circom` with the MIT Poseidon include; capture the resulting R1CS and circuit hash
- [ ] 1.3 Diff the recompiled R1CS / circuit hash against the current `ticketcheck-v1` artifacts
- [ ] 1.4 Record the outcome: identical → reuse existing `.zkey` + backend `verification_key.json`; divergent → schedule a fresh phase-2 trusted setup + backend vkey deploy

## 2. Verification Gate 2 — browser prover viability (decides Path A feasibility & threading)

- [ ] 2.1 (a) Spike `ark-circom`/arkworks circom Groth16 proving in a pure-browser WASM build (no native bindings), reusing the existing `ticketcheck.wasm` witness calculator and `.zkey`; confirm it produces a proof in a Web Worker for a known input
- [ ] 2.2 (b) Evaluate the threading model: attempt multithreaded `wasm-bindgen-rayon` and verify whether COOP/COEP cross-origin isolation can be enabled without breaking Service Worker registration, CSP, or third-party embeds (PostHog etc.); also benchmark the single-threaded fallback
- [ ] 2.3 (c) Measure prover JS + WASM bundle size and real proof-generation time on representative mobile browsers (mid- and low-end); A/B against the current snarkjs baseline (~2 s in-browser)
- [ ] 2.4 (d) Confirm the prover's proof + public-signals output is accepted by `vocdoni/circom2gnark` → `gnark.Verify`; if the native serialization differs, prototype the thin snarkjs-format JSON adapter
- [ ] 2.5 Decide `ark-circom` directly (hand-rolled `wasm-bindgen` wrapper) vs via mopro adapter, based on maintenance/bundle trade-off
- [ ] 2.6 Record gate 2 outcome (viable / not viable; threaded / single-threaded)

## 3. Decision Checkpoint — Path A vs Path B

- [ ] 3.1 From gates 1 & 2, decide Path A (replace) or Path B (arm's-length interim); update `design.md` Open Questions with the resolution and rationale
- [ ] 3.2 If Path B is chosen as interim, branch to section 8; otherwise proceed with Path A (sections 4–7)

## 4. Path A — Circuit artifacts (vector ②: remove GPL Poseidon)

- [ ] 4.1 Commit the MIT Poseidon include change to `frontend/circuits/ticketcheck-v1/ticketcheck.circom`; remove the `circomlib` GPL dependency from the circuit's `package.json`
- [ ] 4.2 Regenerate `public/circuits/ticketcheck-v1/ticketcheck.wasm` and `ticketcheck.zkey` (reuse existing `.zkey` if gate 1 was identical; otherwise run the new trusted setup)
- [ ] 4.3 Regenerate the SHA-256 circuit-integrity manifest to match the new artifacts
- [ ] 4.4 If the R1CS diverged, deploy the new `verification_key.json` to the backend in lockstep (cross-repo coordination)

## 5. Path A — Proving runtime (vector ①: remove snarkjs)

- [ ] 5.1 Add the arkworks-based WASM prover (MIT/Apache) and its build step to the frontend pipeline; keep the Rust→WASM build behind a single make target
- [ ] 5.2 Replace `groth16.fullProve` in `src/workers/proof.worker.ts` with the new prover, keeping the worker's `postMessage` request/result contract stable
- [ ] 5.3 Add the snarkjs-format proof-JSON adapter in the worker / `proof-service.ts` if gate 2(d) showed a serialization mismatch
- [ ] 5.4 Remove the `snarkjs` module declaration from `src/resource.d.ts`
- [ ] 5.5 Apply the chosen threading decision (multithreaded + COOP/COEP, or single-threaded fallback) per gate 2(b)

## 6. Path A — Cross-origin isolation (only if multithreaded)

- [ ] 6.1 Add COOP/COEP headers in the Caddyfile / hosting config; reconcile with the existing CSP
- [ ] 6.2 Verify Service Worker registration, circuit caching, and required third-party embeds still function under isolation

## 7. Path A — Remove GPL, verify, and ship

- [ ] 7.1 Remove `snarkjs` (and transitive `ffjavascript`) from `package.json`; run `make check`
- [ ] 7.2 Run a dependency license audit over the production frontend deps and confirm zero GPL-family licenses in the shipped runtime
- [ ] 7.3 End-to-end test: generate a proof with the new runtime and verify it round-trips through `VerifyEntry` (unchanged backend, or newly-keyed backend if vkey changed)
- [ ] 7.4 Update the OSS-license inventory to reflect the removed GPL deps (hand-off note to the separate OSS-license-page change)
- [ ] 7.5 Open the frontend PR (and backend PR if vkey changed); merge after CI; ship to dev, then cut the production release so the GPL-free bundle reaches prod

## 8. Path B — Arm's-length interim (only if chosen at 3.2)

- [ ] 8.1 Configure the bundler so the `snarkjs` proving worker builds as a separate chunk and is never inlined into the main app chunk
- [ ] 8.2 Add the GPL-3.0 written source offer + full license text to the distributed app and the OSS-license surface
- [ ] 8.3 Document the arm's-length boundary as a build invariant (guard against future bundler changes that would inline snarkjs) and schedule Path A as the follow-up end state
