## ADDED Requirements

### Requirement: Ethereum address validation

The entity package SHALL provide a `ValidateEthereumAddress(addr string) error` function that validates an Ethereum address format.

The function SHALL return nil when the address matches the pattern `^0x[0-9a-fA-F]{40}$`, and return an error otherwise.

#### Scenario: Valid checksummed address

- **WHEN** ValidateEthereumAddress receives "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"
- **THEN** it returns nil

#### Scenario: Valid lowercase address

- **WHEN** ValidateEthereumAddress receives "0x742d35cc6634c0532925a3b844bc9e7595f2bd18"
- **THEN** it returns nil

#### Scenario: Missing 0x prefix

- **WHEN** ValidateEthereumAddress receives "742d35cc6634c0532925a3b844bc9e7595f2bd18"
- **THEN** it returns an error mentioning "Ethereum address"

#### Scenario: Too short

- **WHEN** ValidateEthereumAddress receives "0x742d35cc"
- **THEN** it returns an error mentioning "Ethereum address"

#### Scenario: Empty string

- **WHEN** ValidateEthereumAddress receives ""
- **THEN** it returns an error mentioning "Ethereum address"

#### Scenario: Invalid hex characters

- **WHEN** ValidateEthereumAddress receives "0xZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ"
- **THEN** it returns an error mentioning "Ethereum address"
