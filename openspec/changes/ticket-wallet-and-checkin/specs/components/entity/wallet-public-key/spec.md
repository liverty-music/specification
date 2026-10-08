# Spec Delta

## Purpose

A WalletPublicKey is the public half of a key pair that a fan's device creates for showing tickets. The private half never leaves that device; the platform keeps only this public key and checks AdmissionCodes against it. A User has at most one active key, so tickets can be shown from one device at a time.

| attribute | meaning | constraint |
|-----------|---------|------------|
| id | the key's identity | required, assigned on registration |
| user | the User whose device created the key | required |
| public key | the public key, ECDSA over P-256 | required, a valid point on the curve |
| status | lifecycle | Active or Replaced |
| registered time | when the device registered it | required |
| replaced time | when a newer key of the same User replaced it | absent while Active |

```mermaid
erDiagram
  User ||--o{ WalletPublicKey : "registers"
```

```mermaid
stateDiagram-v2
  [*] --> Active
  Active --> Replaced
  Replaced --> [*]
```

## ADDED Requirements

### Requirement: A public key is a valid P-256 key

A WalletPublicKey's public key SHALL be a valid ECDSA public key on the P-256 curve.

#### Scenario: Key from a browser

- **WHEN** the public key exported by a browser for a new P-256 signing key pair is given
- **THEN** it is valid

#### Scenario: Not a curve point

- **WHEN** 65 random bytes are given as the public key
- **THEN** it is invalid

### Requirement: A new key starts Active

A new WalletPublicKey SHALL start Active with no replaced time.

#### Scenario: New key

- **WHEN** a WalletPublicKey is registered
- **THEN** it is Active
