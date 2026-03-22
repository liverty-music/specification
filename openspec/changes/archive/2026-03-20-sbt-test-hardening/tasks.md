## 1. Contract Changes

- [x] 1.1 Override `approve` in TicketSBT.sol to revert with "SBT: Ticket transfer is prohibited"
- [x] 1.2 Override `setApprovalForAll` in TicketSBT.sol to revert with "SBT: Ticket transfer is prohibited"

## 2. Test Additions — Approve & Transfer Blocking

- [x] 2.1 Add test: `approve` reverts for token owner
- [x] 2.2 Add test: `setApprovalForAll` reverts for token owner
- [x] 2.3 Add test: 3-argument `safeTransferFrom` reverts

## 3. Test Additions — Edge Cases

- [x] 3.1 Add test: duplicate mint (same tokenId) reverts
- [x] 3.2 Add test: mint to `address(0)` reverts

## 4. Test Additions — supportsInterface (ERC-165)

- [x] 4.1 Add test: returns true for ERC-721 interfaceId
- [x] 4.2 Add test: returns true for ERC-5192 interfaceId
- [x] 4.3 Add test: returns true for IAccessControl interfaceId
- [x] 4.4 Add test: returns false for unsupported interfaceId (`0xffffffff`)

## 5. Test Additions — AccessControl Role Management

- [x] 5.1 Add test: admin grants MINTER_ROLE to new address
- [x] 5.2 Add test: admin revokes MINTER_ROLE, revoked address cannot mint
- [x] 5.3 Add test: non-admin cannot grant MINTER_ROLE

## 6. Test Additions — Constructor Verification

- [x] 6.1 Add test: `name()` returns "Liverty Music Ticket", `symbol()` returns "LMTKT"
- [x] 6.2 Add test: deployer has DEFAULT_ADMIN_ROLE and MINTER_ROLE

## 7. Fuzz Tests

- [x] 7.1 Add `testFuzz_MintAnyTokenId(uint256 tokenId)` — mint succeeds for arbitrary tokenId
- [x] 7.2 Add `testFuzz_UnauthorizedMintReverts(address caller)` — arbitrary non-minter cannot mint

## 8. CI — Slither Integration

- [x] 8.1 Add `slither` job to `.github/workflows/test.yml` under contracts path filter
- [x] 8.2 Create `contracts/slither.config.json` with initial configuration
- [x] 8.3 ~~Run Slither locally~~ → CI-only execution; triage findings on first CI run

## 9. CI — Gas Snapshot & Fuzz Depth

- [x] 9.1 Run `forge snapshot` to generate `contracts/.gas-snapshot` and commit to git
- [x] 9.2 Add `forge snapshot --check` step to forge-test CI job
- [x] 9.3 Update forge-test CI job to use `--fuzz-runs 10000`

## 10. Verification

- [x] 10.1 Run `forge test -vvv` locally — all 23 tests pass
- [x] 10.2 ~~Run Slither locally~~ → CI-only; verify on first PR CI run
- [ ] 10.3 Verify CI pipeline runs successfully with new jobs
