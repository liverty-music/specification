## REMOVED Requirements

### Requirement: Distributed bundle contains no copyleft-licensed code
**Reason**: The browser-side ZK proving runtime and circuit artifacts are removed with the ZKP entry flow under the Scenario A pivot; there is no shipped proving bundle to license-constrain.
**Migration**: None; the `prover/`, `circuits/`, and `public/circuits/` artifacts are deleted.

### Requirement: Client-generated proofs remain verifiable by the gnark backend
**Reason**: Both the client prover and the backend `gnark`/`circom2gnark` verifier are removed.
**Migration**: None; code and dependencies deleted.

### Requirement: Proof generation stays on-device
**Reason**: No ZK proof is generated anymore.
**Migration**: None; code deleted.

### Requirement: Offline proof generation is preserved
**Reason**: No ZK proof is generated anymore; offline entry (if needed) will be handled by an offline-verifiable signed QR in the Web2 design.
**Migration**: None; code deleted.

### Requirement: Circuit artifact integrity is verified before use
**Reason**: No circuit artifacts are served.
**Migration**: None; artifacts deleted.

### Requirement: Cross-origin isolation when multithreaded proving is used
**Reason**: No multithreaded WASM prover is served, so the COOP/COEP requirement no longer applies.
**Migration**: None; the proving runtime is deleted.
