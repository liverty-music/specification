# ZKP Browser Client Libraries Research

> Researched: 2026-02-20

## Summary

`circom + snarkjs` is the only production-ready option for browser-based Groth16 proof generation
compatible with a gnark Go verifier. All alternatives (Noir, halo2, plonky2/3) use different proof
systems and cannot interoperate with gnark's Groth16 verifier.

## Libraries

### 1. circom + snarkjs — RECOMMENDED

| Field | Value |
|---|---|
| snarkjs version | 0.7.5 (October 18, 2024; ~15 months quiet as of Feb 2026) |
| Weekly npm downloads | ~19,000 |
| Proof systems | Groth16, PLONK, FFLONK (beta) |

**Browser WASM support**: Full and battle-tested. Pure JS + WASM ES module.

**Proof generation time (Merkle depth 20 with Poseidon)**:
- Desktop: **3–8 seconds** (2024 arxiv benchmark `2409.01976`)
- Mobile: 8–15s (mid-range), 30–60s (low-end Android)
- Poseidon2 hashing reduces time ~60% vs MiMC for equivalent circuits

**Bundle sizes**:
- snarkjs JS: ~1–1.5 MB
- Circuit `.wasm` (depth-20 Merkle): ~200–500 KB
- `.zkey` proving key: **5–30 MB** (dominant cache concern)

**Offline capability**: Full. `.wasm` + `.zkey` are normal binary assets cacheable by Service Worker.

**gnark compatibility**: Via `vocdoni/circom2gnark` adapter (production-tested by Vocdoni voting).

**Ecosystem**: Polygon ID, Semaphore, Tornado Cash. circomlib provides Poseidon, MiMC, Merkle,
nullifier templates.

**Risk**: Library in slow-maintenance mode since v0.7.5. iden3 team's focus shifted toward
identity products. Format is stable; no expected breaking changes.

---

### 2. Noir (Aztec) — REJECTED

| Field | Value |
|---|---|
| Version | 1.0 pre-release (beta.18, late 2025) |
| Default proof system | UltraHonk / UltraPlonk (NOT Groth16) |
| bb.js WASM bundle | ~25–50 MB |

**Groth16 support**: Only via LambdaClass experimental `noir_backend_using_gnark` — WIP, Groth16
side non-functional as of Feb 2026.

**Verdict**: Incompatible with gnark Groth16 verifier. Rejected.

---

### 3. halo2 — REJECTED

- PSE fork entered maintenance mode January 2025
- Uses Halo2 proof system, not Groth16 → incompatible with gnark verifier
- WASM proof generation: ~10s mobile (single-threaded, rayon falls back)

---

### 4. plonky2 / plonky3 — REJECTED

- FRI-based STARKs, not Groth16
- No stable browser WASM SDK as of Feb 2026

---

### 5. gnark-WASM (vocdoni PoC) — NOT YET PRODUCTION

`vocdoni/gnark-wasm-prover` compiles gnark's Groth16 prover to WASM via TinyGo + LLVM. Eliminates
the circom2gnark translation layer. However:
- Research-grade proof-of-concept only
- Circuit authoring requires Go (not circom)
- WASM binary much larger than snarkjs + circuit WASM

**Watch for**: mopro (github.com/zkmopro/mopro) issue #290 tracks wasm-bindgen browser support.
If this lands in 2026, arkworks + rust-witness WASM could replace snarkjs with 10–20x faster
proving and compatible Groth16 output.

---

## Decision Matrix

| Criterion | circom+snarkjs | Noir+bb.js | halo2 | gnark-WASM |
|---|---|---|---|---|
| Groth16 output | Yes | No | No | Yes |
| Browser WASM | Yes (production) | Yes | Partial | PoC only |
| Offline (Service Worker) | Yes | Yes | Partial | No |
| gnark Go verifier compat | Yes (circom2gnark) | No | No | Yes (native) |
| Proof time Merkle/20 | 3–8s desktop | Unknown | ~10s mobile | Unknown |
| Circuit WASM size | 200–500 KB | ~25–50 MB | Large | Large |
| .zkey / SRS size | 5–30 MB | ~10–20 MB | — | — |

---

## Implementation Notes

- Use **Poseidon** (not MiMC, not Pedersen) for Merkle tree and nullifier hashing
- Keep tree depth **≤ 20** to stay under 30s on low-end mobile
- Cache `.zkey` and circuit `.wasm` via Service Worker **runtime cache** (not precache):
  - .zkey exceeds Workbox's 2MB precache limit
  - Use versioned CDN URLs + CacheFirst strategy
  - Use Workbox `injectManifest` mode for custom routing
- Run proof generation in a **Web Worker** (snarkjs uses Web Workers for WASM threading)

## Sources

- [iden3/snarkjs GitHub](https://github.com/iden3/snarkjs)
- [Benchmarking ZKP hash functions (arxiv 2409.01976)](https://arxiv.org/pdf/2409.01976)
- [vocdoni/circom2gnark](https://github.com/vocdoni/circom2gnark)
- [vocdoni gnark-wasm-prover](https://github.com/vocdoni/gnark-wasm-prover)
- [lambdaclass/noir_backend_using_gnark](https://github.com/lambdaclass/noir_backend_using_gnark)
- [mopro wasm-bindgen issue #290](https://github.com/zkmopro/mopro/issues/290)
- [ZKP Frameworks Survey (arXiv 2502.07063)](https://arxiv.org/html/2502.07063v1)
