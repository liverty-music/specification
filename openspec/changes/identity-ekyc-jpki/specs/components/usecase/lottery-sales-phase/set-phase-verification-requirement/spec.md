## ADDED Requirements

### Requirement: Verification lane, per-event requirement, and fallback

Verification SHALL be **optional by default** (`UNVERIFIED`). An
Organizer/administrator MAY mark an **event or lottery phase as requiring a verified
identity**. **MVP scope (2026-09-02): verification-required events are JPKI-only** —
only JPKI-verified (strong-dedupe) fans may apply, and non-card-holders are excluded
by design (the 任意/平等 fairness of this is a legal-review item). Unverified fans
SHALL be **clearly informed** of the requirement and how to satisfy it (JPKI).

**POST-MVP:** a **運転免許証 IC fallback** (Pocket Sign's separate **Verify CardInfo**
product) for non-card fans, which would be **substantively non-disadvantaging**.
**Honest limitation (why it is deferred, not free):** the driver's licence path
proves identity but **does not yield an equivalent stable per-person dedupe key**
(only a document number, which can change) — so a licence-fallback account has a
**weaker 1-person guarantee** and does not advance the anti-scalp core. When added,
each organizer would choose per event to accept the fallback (flag/limit such
accounts) or require JPKI-only. The proto keeps the `DRIVER_LICENCE`/`WEAK`/
`VERIFIED_ANY` values for this forward-compat.

#### Scenario: A verification-required event is JPKI-only (MVP)

- **WHEN** an organizer marks a phase as requiring verification
- **THEN** only JPKI-verified (strong-dedupe) fans may apply, and no weaker fallback is offered (MVP is JPKI-only)

#### Scenario: Licence fallback is offered with a weaker-dedupe flag (POST-MVP)

- **WHEN** (post-MVP) an event allows the 運転免許証 fallback and a non-card fan uses it
- **THEN** they gain verified standing for that event without material disadvantage, and the account is flagged as having a weaker (document-scoped) dedupe

#### Scenario: Unverified fan is clearly informed

- **WHEN** an `UNVERIFIED` fan encounters an event that requires verification
- **THEN** the system clearly informs them of the requirement and how to complete JPKI verification before applying
