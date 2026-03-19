## 0. Prerequisites

- [ ] 0.1 Confirm Phase 1 (sbt-test-hardening) is fully complete and merged

## 1. Halmos Setup & Proofs

- [ ] 1.1 Add Halmos to dev dependencies (`pip install halmos`) and document in README
- [ ] 1.2 Create `test/halmos/TicketSBT.halmos.t.sol` with Halmos test structure
- [ ] 1.3 Implement `check_transferFromAlwaysReverts` — prove transferFrom reverts for all inputs
- [ ] 1.4 Implement `check_safeTransferFromAlwaysReverts` — prove both safeTransferFrom overloads revert
- [ ] 1.5 Implement `check_approveAlwaysReverts` — prove approve reverts for all inputs
- [ ] 1.6 Implement `check_setApprovalForAllAlwaysReverts` — prove setApprovalForAll reverts
- [ ] 1.7 Implement `check_unauthorizedMintReverts` — prove non-minter mint always reverts
- [ ] 1.8 Implement `check_lockedAlwaysTrueForMinted` — prove locked() returns true for all minted tokens
- [ ] 1.9 Run Halmos locally and verify all proofs pass

## 2. Foundry Invariant Tests

- [ ] 2.1 Create `test/invariant/Handler.sol` with bounded mint operations and ghost variables
- [ ] 2.2 Create `test/invariant/TicketSBT.invariant.t.sol` with invariant test contract
- [ ] 2.3 Implement `invariant_noTokenTransferred` — ownerOf never changes after mint
- [ ] 2.4 Implement `invariant_allTokensLocked` — locked() is true for every minted token
- [ ] 2.5 Implement `invariant_mintCountMatchesBalances` — total minted equals sum of balanceOf
- [ ] 2.6 Configure `foundry.toml` with invariant test settings (runs, depth)
- [ ] 2.7 Run invariant tests locally and verify all pass

## 3. Aderyn Integration

- [ ] 3.1 Install Aderyn and verify it runs against the project
- [ ] 3.2 Add `aderyn` job to `.github/workflows/test.yml` parallel to Slither
- [ ] 3.3 Create `.aderyn.toml` with project config and initial exclusions
- [ ] 3.4 Triage initial Aderyn findings and exclude false positives

## 4. Mutation Testing

- [ ] 4.1 Install vertigo-rs and verify compatibility with current Foundry version
- [ ] 4.2 Run vertigo-rs locally against TicketSBT and the full test suite
- [ ] 4.3 Analyze surviving mutants and add missing tests if gaps are found
- [ ] 4.4 Add weekly/manual-dispatch CI job for mutation testing

## 5. Coverage Reporting

- [ ] 5.1 Run `forge coverage --report lcov` locally and review results
- [ ] 5.2 Add coverage job to CI that uploads lcov as artifact

## 6. CI Integration

- [ ] 6.1 Add Halmos CI job (PR to main trigger) to `.github/workflows/test.yml`
- [ ] 6.2 Verify all new CI jobs (Halmos, Aderyn, coverage) run successfully
- [ ] 6.3 Document the full security toolchain in contracts/README.md

## 7. Verification

- [ ] 7.1 Run full test suite locally: unit + fuzz + invariant + Halmos — all pass
- [ ] 7.2 Run Slither + Aderyn locally — no unresolved high/medium findings
- [ ] 7.3 Run mutation testing — zero or minimal surviving mutants
- [ ] 7.4 Verify CI pipeline with all new jobs runs end-to-end
