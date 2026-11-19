# Spec Delta

## MODIFIED Requirements

### Requirement: The scanner binds to the first device

Open SHALL take a link token, the device's public key, a call signature with its sign time, and the current time. It SHALL find the Scanner with Scanner.GetByLinkToken and fail with PermissionDenied when no Scanner holds the link token. Before binding, it SHALL check that the call is proven by the given public key, and fail with PermissionDenied without binding when it is not, so a Scanner is only ever bound to a key whose private key the device holds. It SHALL then bind the Scanner with Scanner.BindDevice, failing with PermissionDenied when BindDevice reports Revoked, without telling it apart from an unknown link token, and with FailedPrecondition when BindDevice reports OtherDevice.

#### Scenario: Staff open the link for the first time

- **WHEN** the link of an Unused Scanner is opened on a device at 14:10
- **THEN** the Scanner is bound to that device's public key and Open succeeds

#### Scenario: Signature from another key

- **WHEN** the link of an Unused Scanner is opened with a public key and a signature made with a different private key
- **THEN** Open fails with PermissionDenied and the Scanner stays Unused

#### Scenario: Link forwarded to another device

- **WHEN** the link of a Scanner bound to one device is opened on another device
- **THEN** Open fails with FailedPrecondition and the Scanner stays bound to the first device

#### Scenario: Revoked scanner

- **WHEN** the link of a Revoked Scanner is opened
- **THEN** Open fails with PermissionDenied

#### Scenario: Unknown link token

- **WHEN** no Scanner holds the link token
- **THEN** Open fails with PermissionDenied
