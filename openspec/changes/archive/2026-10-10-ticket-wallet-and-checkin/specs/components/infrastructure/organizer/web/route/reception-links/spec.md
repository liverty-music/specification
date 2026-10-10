# Spec Delta

## Purpose

The organizer console screen where an operator prepares reception for one published event: issuing a link per reception device, seeing which links are in use, and revoking or reissuing them.

## ADDED Requirements

### Requirement: One link per device

The screen SHALL list the event's ReceptionLinks by number, labelled 受付1, 受付2 and so on, with their state: 未使用 (unused), 使用中 (in use) with the time it was first opened, or 取り消し済み (revoked). It SHALL let the operator issue a link with one action, without asking for a name, and show the new link's URL with actions to copy and share it. The URL SHALL be on the reception origin, which is separate from the console origin, and carry the token in its fragment (`https://reception.liverty-music.app/#<token>`), so that the token never reaches a web server or its access logs. It SHALL show the event's reception window and that each link works on the first device that opens it only, and offer a link to the reception guide, opened in a new tab, to hand to venue staff with the links.

#### Scenario: Issue two links

- **WHEN** an operator issues two links for an event without links
- **THEN** `受付1` and `受付2` are listed as 未使用, each with a URL to copy

#### Scenario: Link opened by staff

- **WHEN** staff open `受付1` at 14:10
- **THEN** the screen shows `受付1` as 使用中 since 14:10 and no longer shows its URL

### Requirement: Revoke and reissue in one step

For a link that is not revoked the screen SHALL offer to revoke it, and to revoke and reissue it, which revokes the link and issues a new one, showing its URL. Both SHALL ask for confirmation first.

#### Scenario: Staff changed phones

- **WHEN** the operator revokes and reissues `受付1` of an event with links 1 and 2, and confirms
- **THEN** `受付1` is 取り消し済み and a new 未使用 `受付3` is shown with its URL

#### Scenario: Unpublished event

- **WHEN** the operator opens the screen for a DRAFT event
- **THEN** the screen says the event must be published before links can be issued

#### Scenario: Event without a start time

- **WHEN** the operator opens the screen for a published event without a start time
- **THEN** the screen says the event needs a start time before links can be issued
