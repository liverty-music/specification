## 1. Legal / docs

- [ ] 1.1 Draft the **暴排条項** (antisocial-forces exclusion clause: R&W + immediate termination) for the Organizer onboarding agreement
- [ ] 1.2 Make acceptance of the clause a condition of onboarding

## 2. Specification (only if a proto is added)

- [ ] 2.1 (if used) additive admin RPC to record the check (e.g. `RecordAntisocialCheck`) in `rpc/admin/organizer/v1` — do NOT alter shipped messages; `buf lint/format/breaking` pass; merge → Release → BSR gen

## 3. Backend

- [ ] 3.1 Additive Atlas migration: antisocial-check fields on `organizers` (`antisocial_check_status`, `reviewer`, `checked_at`) — ALTER the shipped table
- [ ] 3.2 Record-check usecase + admin handler (admin-role gated); persist reviewer/timestamp/result
- [ ] 3.3 Gate: a **passing** check is a precondition to create/activate an Organizer; a hit (or no check) blocks
- [ ] 3.4 Deactivation-on-discovery reuses the existing `deactivated` hook; record the reason
- [ ] 3.5 Tests: pass→allow, hit→block, no-check→block, record retained; `make check` passes

## 4. Frontend (admin console)

- [ ] 4.1 反社チェック step in the organizer-management screen: record result before create; block on hit; show the retained record
- [ ] 4.2 `make check` passes

## 5. Release & ship to prod

- [ ] 5.1 Land AFTER `organizer-accounts` (this ALTERs its table + gates its Create)
- [ ] 5.2 Backend + frontend PRs merged → release → prod
- [ ] 5.3 Verify in prod: an admin records a passing 反社チェック → Organizer can be created; a hit blocks; later discovery deactivates; records retained for audit
