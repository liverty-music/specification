## Why

The frontend bundle distributed to every fan's browser contains GPL-3.0 code through two paths: the proving runtime (`snarkjs` + `ffjavascript`, imported by `proof.worker.ts`) and the circuit artifacts (`ticketcheck.wasm` / `ticketcheck.zkey`, compiled from `circomlib`'s GPL-3.0 `poseidon.circom`). Serving a JavaScript/WASM bundle that embeds this code is distribution under the GPL, which is incompatible with shipping Liverty as a proprietary, app-store-bound product. The license was never evaluated when `snarkjs` was selected; the original choice was driven purely by it being the only production-ready browser Groth16 prover compatible with the `gnark` backend verifier. The original design research already named `arkworks` as the intended successor once browser WASM tooling matured — that tooling (mopro / `wasm-bindgen`) has now landed, so this is the planned upgrade, not a risky deviation.

## What Changes

- Replace the client-side proving runtime `snarkjs` (GPL-3.0) with an `arkworks` / `ark-circom`-based prover (MIT/Apache-2.0) compiled to WASM, reusing the existing circom `.wasm` witness calculator and `.zkey` proving key.
- Replace the GPL-3.0 `circomlib` `poseidon.circom` include with a permissively-licensed (MIT) Poseidon source and recompile the circuit artifacts, so the distributed `.wasm` / `.zkey` derive from non-copyleft sources.
- Preserve the hard invariant that generated proofs remain verifiable by the existing `gnark` + `vocdoni/circom2gnark` backend (BN254 Groth16, snarkjs-compatible proof JSON) — backend verification stays unchanged when the proof format and verification key are preserved.
- Preserve offline proof generation (Service Worker caching of prover WASM + circuit artifacts) and SHA-256 circuit-integrity verification; regenerate integrity hashes after recompilation.
- **BREAKING** (build/deploy, not API): adopting multithreaded WASM proving (`wasm-bindgen-rayon`) requires cross-origin isolation (COOP/COEP) headers — a hosting/CSP change. A single-threaded fallback avoids this at a performance cost; the threading decision is an open decision resolved by the verification gates.
- Two verification gates precede the irreversible swap and decide final cost/approach: (1) whether the MIT-Poseidon recompile yields an identical R1CS so existing `.zkey`/verification key can be reused, and (2) whether the `ark-circom` browser WASM prover is production-viable for a PWA (threading model, bundle/WASM size, real mobile-browser proof time, proof-JSON compatibility).

## Capabilities

### New Capabilities
- `client-zk-proving`: The browser-side zero-knowledge proving runtime — its license constraint (no copyleft code in the distributed bundle), its output contract (gnark-verifiable BN254 Groth16), offline capability, and circuit-integrity verification. Currently implicit in the ticket-system MVP; this change makes it explicit and removes the GPL dependency.

### Modified Capabilities
<!-- zkp-entry (backend EntryService RPC contracts) is library-agnostic and unchanged.
     frontend-hosting may gain a conditional cross-origin-isolation requirement only if
     multithreaded WASM is adopted; that decision is deferred to design.md, so no delta
     spec is forced here. -->

## Impact

- **Frontend code**: `src/workers/proof.worker.ts` (prover swap), `src/services/proof-service.ts` (worker invocation / proof serialization adapter), `src/resource.d.ts` (drop `snarkjs` module decl).
- **Dependencies**: remove `snarkjs` + transitive `ffjavascript` (GPL-3.0); add `ark-circom` / mopro-based WASM prover (MIT/Apache); new Rust→WASM build step (`wasm-bindgen`) in the frontend pipeline.
- **Circuit artifacts**: `frontend/circuits/ticketcheck-v1/ticketcheck.circom` (poseidon include source), regenerated `public/circuits/ticketcheck-v1/ticketcheck.wasm` + `ticketcheck.zkey`, and their SHA-256 integrity manifest.
- **Backend**: `internal/infrastructure/zkp/verifier.go` — unchanged if the verification key and proof JSON format are preserved; requires a new `verification_key.json` only if the R1CS changes (verification gate 1).
- **Hosting / PWA**: Caddyfile / CSP and Service Worker caching, plus conditional COOP/COEP cross-origin-isolation headers if multithreaded WASM proving is adopted.
- **Out of scope**: the OSS-license page UI and the legal three-set (terms / privacy / OSS licenses) are tracked as a separate change.
