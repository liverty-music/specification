# OSS-license inventory hand-off (for the separate OSS-license-page change)

This change (`remove-gpl-zk-prover`) removed all GPL-3.0 code from the distributed
frontend bundle. The OSS-license page / legal three-set change should reflect:

## Removed (no longer shipped — drop from any license listing)
- `snarkjs` (GPL-3.0) — was the browser Groth16 prover.
- `ffjavascript` (GPL-3.0) — transitive finite-field lib of snarkjs.
- `circomlib` / `circomlibjs` (GPL-3.0) — were build-time circuit deps (Poseidon); never re-added.

## Added (permissive — include in the OSS-license listing)
The browser prover is now an in-repo Rust→WASM crate (`frontend/prover/`) compiled to
`frontend/prover/pkg/`. The shipped `ticketcheck_prover_bg.wasm` is built from:

| Component | License | Notes |
|---|---|---|
| arkworks (`ark-bn254`, `ark-groth16`, `ark-ec`, `ark-ff`, `ark-serialize`, `ark-std`, `ark-relations`, `ark-snark`) | MIT OR Apache-2.0 | Groth16 prover + BN254 |
| `ark-circom` (vendored at `frontend/prover/vendor/ark-circom`, `parallel` stripped) | MIT OR Apache-2.0 | circom witness calc + zkey reader |
| `wasmer` (`js-default`) | MIT | runs the circom witness `.wasm` via the browser WASM engine |
| `wasm-bindgen`, `getrandom("js")`, `num-bigint`, `serde_json` | MIT OR Apache-2.0 | glue / utils |

## Circuit artifacts
`frontend/circuits/ticketcheck-v1/poseidon.circom` + `poseidon_constants.circom` are now
**in-repo MIT** (clean-room regeneration of the public Poseidon reference; see
`POSEIDON_PROVENANCE.md`). The published `public/circuits/ticketcheck-v1/ticketcheck.wasm`
is recompiled from these MIT sources; `.zkey` is reused unchanged (byte-identical R1CS).

## Verified (2026-06-05)
`npx license-checker --production --summary` over the frontend reports **zero GPL-family
licenses** in the shipped runtime (MIT / Apache-2.0 / BSD / ISC / MPL-2.0 only).
