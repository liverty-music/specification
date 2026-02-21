# ZKP Go Backend Verification Libraries Research

> Researched: 2026-02-20

## Summary

The Go ZKP library ecosystem is thin. For Groth16 on BN254 (the curve used by circom/snarkjs),
the only production-credible options are `gnark` and `go-rapidsnark/verifier`. All others are
abandoned or unsuitable.

## Libraries

### 1. gnark (github.com/consensys/gnark) — RECOMMENDED

| Field | Value |
|---|---|
| Latest version | v0.14.0 (August 22, 2024) |
| gnark-crypto companion | v0.15.0 (January 2025) |
| Stars | ~1.7k |
| Go native | Yes (pure Go, no CGO) |
| Production use | Linea zkEVM (ConsenSys), audited by Least Authority Sept 2024 |

**Groth16 support**: Full. `backend/groth16` implements Groth16 for BN254, BLS12-381, BLS12-377, BW6-761.

**snarkjs compatibility**: gnark's native serialization format is NOT the same as snarkjs JSON.
Requires `vocdoni/circom2gnark` adapter (see below). Issue #1582 (Aug 2025) requests native
snarkjs JSON export; not merged as of Feb 2026.

**Performance**: Verification ~1–2ms on BN254. Fastest pairing implementation in Go.

**Limitations**:
- Not constant-time (no side-channel guarantee)
- Pre-1.0 API; minor versions may break
- Carries proving code as dependency even for verify-only use

---

### 2. vocdoni/circom2gnark — REQUIRED ADAPTER

A bridge library that parses circom/snarkjs JSON artifacts and converts them to gnark-native types.

**Usage pattern**:
```go
import "github.com/vocdoni/circom2gnark/parser"

gnarkProof, gnarkVk, gnarkWitness, _ := parser.ConvertCircomToGnark(circomProof, circomVk, circomPub)
err := groth16.Verify(gnarkProof, gnarkVk, gnarkWitness)
```

**Performance**: First call ~880ms (gnark setup); subsequent calls ~1–2ms.

**Limitations**: Small community project; Groth16 BN254 only; depends on gnark so both are imported.

---

### 3. go-rapidsnark/verifier (github.com/iden3/go-rapidsnark) — ALTERNATIVE

| Field | Value |
|---|---|
| Latest version | verifier/v0.0.5, prover/v0.0.15 (November 13, 2025) |
| Language | 92% Go, 5.8% C, 2.2% Assembly (verifier subpackage is pure Go) |

**Advantage**: Reads snarkjs JSON natively (no adapter needed). Built within iden3/Polygon ID
ecosystem.

**Limitations**: License unclear on pkg.go.dev (missing SPDX header). Less battle-tested than
gnark. Sparse documentation.

**Verdict**: Viable alternative if license is confirmed acceptable. Rejected for this project in
favor of gnark + circom2gnark due to license uncertainty.

---

### 4. REJECTED Libraries

| Library | Reason |
|---|---|
| `iden3/go-circom-prover-verifier` v0.0.1 (2020) | Abandoned; requires go-ethereum v1.9.13 |
| `arnaucube/go-bellman-verifier` | GPL-3.0; 7 commits; research-grade only |
| `gnark-crypto` alone | Too low-level; would require hand-rolling Groth16 3-pairing check |

---

## Decision

**Use `consensys/gnark` v0.14.0 + `vocdoni/circom2gnark`.**

Integration test requirement: round-trip a known circom proof through circom2gnark → gnark Verify
before any production deploy, to confirm BN254 field encoding compatibility.

## Sources

- [gnark GitHub](https://github.com/Consensys/gnark)
- [gnark Releases](https://github.com/Consensys/gnark/releases)
- [Least Authority gnark audit (PDF)](https://leastauthority.com/wp-content/uploads/2024/12/Least-Authority-Consensys-Linea-ProverCryptography-Phase-1-Initial-Audit-Report.pdf)
- [vocdoni/circom2gnark](https://github.com/vocdoni/circom2gnark)
- [iden3/go-rapidsnark](https://github.com/iden3/go-rapidsnark)
- [gnark snarkjs JSON compatibility issue #1582](https://github.com/Consensys/gnark/issues/1582)
