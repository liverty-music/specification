# Reconcile Provisioning

## Purpose

The Organizer domain: the vetted seller an admin creates, its link to the
artists it represents, the runtime provisioning that gives each Organizer an
isolated Zitadel tenant its operator can sign into, and the admin surface to
manage them. The organizer-facing API and console are separate capabilities.

## Requirements

### Requirement: Organizer provisioning is idempotent and compensating

Creating an Organizer SHALL be idempotent and compensating across the
tenant-provisioning steps (tenant org, login policy, project grant, operator
+ owner grant, and the persisted `zitadel_org_id`). A retry after a partial
failure SHALL complete provisioning without creating a duplicate Organizer or
duplicate tenant org, and SHALL never leave the Organizer without a `owner`
operator.

#### Scenario: Retry after mid-provisioning failure does not duplicate

- **WHEN** a `Create` is retried after failing partway through provisioning
- **THEN** the system SHALL complete the remaining steps without creating a
  second Organizer or a second tenant org

#### Scenario: Operator is never left without an owner grant

- **WHEN** provisioning completes for an Organizer
- **THEN** the Organizer SHALL have at least one operator holding the
  `owner` role
