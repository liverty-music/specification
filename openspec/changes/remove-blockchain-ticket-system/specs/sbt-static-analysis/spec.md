## REMOVED Requirements

### Requirement: Slither static analysis in CI
**Reason**: The `contracts/` directory and all Solidity sources are removed under the Scenario A pivot, so the contract-CI gate has nothing to analyze.
**Migration**: None; remove the `slither` CI job together with `contracts/`.

### Requirement: Gas regression detection
**Reason**: No Solidity contracts remain, so `forge snapshot` has no target.
**Migration**: None; remove the `forge snapshot --check` step and `.gas-snapshot`.

### Requirement: Increased fuzz depth in CI
**Reason**: No Foundry tests remain.
**Migration**: None; remove the `forge-test` CI job.
