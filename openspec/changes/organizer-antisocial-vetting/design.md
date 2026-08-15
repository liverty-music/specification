## Context

See proposal.md - Why. Legal basis + owner in `docs/payments-design.md`
(Regulatory compliance #6) and issue #778. This layers a vetting precondition
onto the already-shipping `organizer-accounts` Create / `deactivated` flow;
that change's capability spec is still in-flight, so this expresses the gate
in its own capability and integrates at archive time. **Do not edit the
`organizer-accounts` change dir** (near-complete, owned by another workstream).

## Goals / Non-Goals

**Goals:** an onboarding 暴排条項, an admin 反社チェック gate before activation,
and deactivation on later discovery — the minimum to exclude 反社会的勢力.

**Non-Goals:** automated third-party screening integration (manual/risk-based
for MVP); the payment 収納代行 scheme; self-serve onboarding.

## Decisions

**D1 — Manual, risk-based check for MVP.** An admin records a name-screening
outcome; no third-party screening API integration yet (a future hardening).
The exemption from liability comes from the 暴排条項 + a documented check, not
from a specific vendor.

**D2 — Additive data, no change to the shipped organizer proto/service.**
Record the check as **additive** fields on the Organizer (e.g.
`antisocial_check_status` / `reviewer` / `checked_at`) via an **ALTER**
migration on the `organizers` table (shipped by `organizer-accounts`), plus a
small admin action to record the result. Do **not** alter the shipped
`rpc/admin/organizer/v1` messages; add a new admin RPC (e.g.
`RecordAntisocialCheck`) or a Create precondition — a follow-up wiring detail,
kept additive so it never conflicts with the in-flight change.

**D3 — Gate at activation, reuse the deactivation hook.** A passing check is a
**precondition** to create/activate; a hit blocks. Post-onboarding discovery
reuses `organizer-accounts`' `deactivated` state (no new teardown path).

## Risks / Trade-offs

- **Manual check is only as good as the operator** → mitigate with the
  documented 暴排条項 (contractual R&W + termination right) so a later-
  discovered tie is a clean termination ground; upgrade to an automated
  screening service later.
- **Ordering vs `organizer-accounts`** → this change must land after
  `organizer-accounts` (it ALTERs its table and gates its Create). Sequence
  accordingly.

## Migration Plan

1. specification: the new capability spec (+ any additive admin RPC) → merge →
   Release → BSR gen (only if a proto is added).
2. backend: additive migration (antisocial-check fields on `organizers`);
   record-check action; make a passing check a create/activation precondition;
   deactivation reason.
3. frontend: a 反社チェック step in the organizer-management screen.
4. legal/docs: 暴排条項 text in the onboarding agreement.
- Rollback: additive columns + additive RPC; drop with no impact on the
  shipped organizer flow.

## Open Questions

- Whether to record the check via a dedicated `RecordAntisocialCheck` admin
  RPC or as a required attestation field on Create — a wiring detail decided at
  implementation; does not change the spec.
