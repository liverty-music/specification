# Spec Delta

## ADDED Requirements

### Requirement: A removed identity is forgotten

90 seconds after the removal removed the identity, the platform SHALL forget it through User.ForgetRemovedIdentity, whether or not a caller waits, trying a step that fails with Unavailable or DeadlineExceeded again. A failure that ends the attempt SHALL be reported to an admin. A removal that did not remove the identity SHALL leave the record.

#### Scenario: Identity removed

- **WHEN** a removal removed the User and its identity
- **THEN** 90 seconds later the identity is no longer recorded as removed

#### Scenario: Identity not removed

- **WHEN** a removal removed the User and ended with User.DeleteIdentity failing
- **THEN** the identity stays recorded as removed
