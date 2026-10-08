# Spec Delta

## Purpose

The organizer console screen where an operator prepares reception for one published event: issuing a named link per reception device, seeing which links are in use, and revoking or reissuing them.

## ADDED Requirements

### Requirement: One named link per device

The screen SHALL list the event's ReceptionLinks with their name and state: 未使用 (unused), 使用中 (in use) with the time it was first opened, or 取り消し済み (revoked). It SHALL let the operator issue a link with a name, suggesting 受付A, 受付B and so on, and show the new link's URL with actions to copy and share it. It SHALL show the event's reception window and that each link works on the first device that opens it only.

#### Scenario: Issue two links

- **WHEN** an operator issues two links for an event without links
- **THEN** `受付A` and `受付B` are listed as 未使用, each with a URL to copy

#### Scenario: Link opened by staff

- **WHEN** staff open `受付A` at 14:10
- **THEN** the screen shows `受付A` as 使用中 since 14:10 and no longer shows its URL

### Requirement: Revoke and reissue in one step

For a link that is not revoked the screen SHALL offer to revoke it, and to revoke and reissue it, which revokes the link and issues a new one with the same name, showing its URL. Both SHALL ask for confirmation first.

#### Scenario: Staff changed phones

- **WHEN** the operator revokes and reissues `受付A` and confirms
- **THEN** the old `受付A` is 取り消し済み and a new 未使用 `受付A` is shown with its URL

#### Scenario: Unpublished event

- **WHEN** the operator opens the screen for a DRAFT event
- **THEN** the screen says the event must be published before links can be issued

#### Scenario: Event without an open time

- **WHEN** the operator opens the screen for a published event without an open time
- **THEN** the screen says the event needs an open time before links can be issued
