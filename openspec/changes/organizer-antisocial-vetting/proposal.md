## Why

A ticketing marketplace that collects money and onboards sellers is expected
(暴力団排除条例, all 47 prefectures; card acquirers demand it) to **exclude
反社会的勢力 (antisocial forces)** from its Organizer relationships. Our
current organizer onboarding (`organizer-accounts`) vets and provisions an
Organizer but has **no 反社 exclusion** — a launch-blocking gap surfaced by
this session's legal sweep (see `docs/payments-design.md` → Regulatory
compliance #6, and issue #778). This change adds that exclusion: a 暴排条項 in
the onboarding agreement and a 反社チェック gate in admin vetting.

## What Changes

- **暴排条項 in the Organizer onboarding agreement** — a representation &
  warranty that the Organizer and its principals are **not** 反社会的勢力 and
  have no such relationships, plus the platform's right to **terminate /
  deactivate immediately** on breach.
- **反社チェック gate in admin vetting** — before an Organizer is
  provisioned/activated, an admin performs a name-screening 反社チェック and
  records the outcome (reviewer, timestamp, result). A **positive hit blocks**
  creation/activation. The record is retained for audit.
- **Post-onboarding discovery → deactivation** — if a 反社 relationship is
  discovered later, an admin deactivates the Organizer, **reusing the existing
  `deactivated` hook** from `organizer-accounts`.

Non-goals: automated/third-party screening-service integration (manual/risk-
based check for MVP); the payment-side 収納代行/legal scheme (payments-design);
self-serve organizer onboarding.

## Capabilities

### New Capabilities
- `organizer-antisocial-exclusion`: the 暴排条項 onboarding clause, the admin
  反社チェック gate on Organizer activation, and post-onboarding deactivation
  on discovery.

### Modified Capabilities
<!-- None edited directly. This layers a vetting precondition onto the
     `organizer-accounts` Create/deactivate flow; that capability's spec is
     still in-flight in its own change, so the gate is expressed here and
     integrates when both archive. Cross-reference, do not edit that change. -->

## Impact

- **specification**: a new `organizer-antisocial-exclusion` capability spec.
  Any proto is **additive** (e.g. an admin RPC to record the check result, or
  a check-status field) and does not alter the shipped
  `rpc/admin/organizer/v1` service.
- **backend**: an **additive** migration adding antisocial-check fields to
  `organizers` (status / reviewer / checked_at); a create/activation
  precondition that a passing check exists; deactivation reason.
- **frontend (admin console)**: a 反社チェック step in the organizer-management
  screen (record result before create; block on hit).
- **legal/docs**: the 暴排条項 text in the Organizer onboarding agreement.
- Depends on `organizer-accounts` (the Create / vetting / `deactivated` flow
  this gates).
