## ADDED Requirements

### Requirement: Distributed bundle contains no copyleft-licensed code

The frontend artifacts served to a fan's browser — the zero-knowledge proving runtime and the circuit artifacts (witness-calculator WASM and proving key) — SHALL NOT contain or be derived from copyleft-licensed (GPL-family) sources. The proving runtime SHALL be licensed under a permissive license (MIT, BSD, or Apache-2.0). The circuit artifacts SHALL be compiled from permissively-licensed circuit sources.

#### Scenario: Proving runtime is permissively licensed

- **WHEN** the production frontend bundle is built and inspected
- **THEN** it SHALL NOT include `snarkjs`, `ffjavascript`, or any other GPL-family package
- **AND** the zero-knowledge proving runtime present SHALL be licensed under MIT, BSD, or Apache-2.0

#### Scenario: Circuit artifacts derive from permissive sources

- **WHEN** the `ticketcheck` circuit is recompiled
- **THEN** every `include`d circuit source (including the Poseidon implementation) SHALL be permissively licensed
- **AND** the published `.wasm` and `.zkey` artifacts SHALL be the output of that permissively-licensed compilation

#### Scenario: License check can be enforced mechanically

- **WHEN** a dependency license audit runs over the distributed frontend dependencies
- **THEN** it SHALL report zero GPL-family licenses in the shipped runtime

### Requirement: Client-generated proofs remain verifiable by the gnark backend

The client-side proving runtime SHALL produce BN254 Groth16 proofs and public signals that the existing backend verifier (`gnark` via `vocdoni/circom2gnark`) accepts. Changing the proving runtime SHALL NOT, by itself, require a backend code change; a backend change SHALL be required only if the circuit's verification key changes.

#### Scenario: Proof round-trips through the unchanged backend

- **WHEN** the new runtime generates a proof for a valid Merkle membership and nullifier, using a circuit whose verification key is unchanged
- **THEN** the backend `VerifyEntry` handler SHALL verify it successfully without modification

#### Scenario: Proof JSON conforms to the backend-parsed format

- **WHEN** a proof is serialized for transport to `VerifyEntry`
- **THEN** its JSON shape SHALL match the snarkjs-compatible format that `vocdoni/circom2gnark` parses
- **AND** any difference in the runtime's native serialization SHALL be normalized to that format before transport

#### Scenario: Verification key change is the only trigger for a backend update

- **WHEN** circuit recompilation yields an R1CS identical to the current artifacts
- **THEN** the existing `.zkey` and backend `verification_key.json` SHALL be reused unchanged
- **WHEN** circuit recompilation yields a different R1CS
- **THEN** a new trusted-setup output SHALL be produced and the backend `verification_key.json` SHALL be updated in lockstep

### Requirement: Proof generation stays on-device

The proving runtime SHALL generate proofs entirely within the browser so that the private input (`trapdoor`) never leaves the fan's device. The runtime SHALL NOT transmit the private input to any server.

#### Scenario: Private input never sent to the server

- **WHEN** a fan generates an entry proof
- **THEN** all witness and proof computation SHALL occur in the browser
- **AND** no request carrying the `trapdoor` or raw witness SHALL be sent to the backend

### Requirement: Offline proof generation is preserved

The proving runtime and circuit artifacts SHALL be cacheable by the Service Worker so that a fan can generate an entry proof without network connectivity at the venue.

#### Scenario: Proof generation works offline

- **WHEN** the prover WASM and circuit artifacts have been cached and the device is offline
- **THEN** the fan SHALL still be able to generate a valid entry proof

### Requirement: Circuit artifact integrity is verified before use

Before using fetched circuit artifacts (`.wasm`, `.zkey`) for proof generation, the runtime SHALL verify each artifact against its expected SHA-256 hash and SHALL refuse to generate a proof if verification fails. Recompiled artifacts SHALL ship with a regenerated integrity manifest.

#### Scenario: Tampered artifact is rejected

- **WHEN** a fetched circuit artifact's SHA-256 hash does not match the expected manifest value
- **THEN** the runtime SHALL NOT generate a proof
- **AND** SHALL surface an integrity error

#### Scenario: Integrity manifest matches recompiled artifacts

- **WHEN** the circuit is recompiled with permissive sources
- **THEN** the SHA-256 integrity manifest SHALL be regenerated to match the new artifacts

### Requirement: Cross-origin isolation when multithreaded proving is used

IF the proving runtime uses multithreaded WASM (shared-memory threading), THEN the application SHALL serve the cross-origin isolation headers (COOP and COEP) required to enable `SharedArrayBuffer`, without breaking Service Worker registration or required third-party embeds. IF cross-origin isolation cannot be enabled compatibly, THEN the runtime SHALL fall back to single-threaded proving.

#### Scenario: Multithreaded proving requires isolation headers

- **WHEN** the runtime is built to use shared-memory WASM threads
- **THEN** the document SHALL be cross-origin isolated (COOP `same-origin` + COEP enforced)
- **AND** Service Worker registration and required embeds SHALL continue to function

#### Scenario: Fallback when isolation is not feasible

- **WHEN** cross-origin isolation would break a required integration
- **THEN** the runtime SHALL use the single-threaded proving path instead
- **AND** SHALL still produce a gnark-verifiable proof
