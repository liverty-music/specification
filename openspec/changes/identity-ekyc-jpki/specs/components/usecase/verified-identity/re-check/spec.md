## Purpose

Periodically re-examines an already-verified identity to detect that its underlying credential has been revoked or its holder's basic details have changed, flagging the account for re-verification rather than silently keeping it verified or hard-locking it.

## ADDED Requirements

### Requirement: 現況確認 (revocation / attribute-change re-check)

The system SHALL periodically use Pocket Sign's **現況確認 (liveness/現況)** check to
detect certificate **revocation or 基本4情報 change (move/name change) / expiry**. On
a revoked/changed result the system SHALL prompt **re-verification** (not a hard
lock), keeping the verified identity fresh without full re-proofing.

#### Scenario: Revoked/changed identity prompts re-verification

- **WHEN** a 現況確認 check reports the certificate is revoked or the 基本4情報 changed
- **THEN** the system flags the account for re-verification (it is not silently kept as verified, and not hard-locked)
