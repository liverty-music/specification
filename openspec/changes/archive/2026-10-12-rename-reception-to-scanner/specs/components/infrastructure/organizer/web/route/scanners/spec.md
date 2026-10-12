# Spec Delta

## Purpose

The organizer console screen where an operator prepares admission for one published event: creating a Scanner per staff device, handing out its link, seeing which Scanners are in use, and revoking or reissuing them.

## ADDED Requirements

### Requirement: One scanner per device

The screen SHALL list the event's Scanners by number, labelled 受付1, 受付2 and so on, with their state: 未使用 (unused), 使用中 (in use) with the time its link was first opened, or 取り消し済み (revoked). It SHALL let the operator create a Scanner with one action, without asking for a name, and show the new Scanner's link with actions to copy and share it. The link SHALL be on the origin of the scanner screen, which is separate from the console origin, and carry the link token in its fragment (`https://reception.liverty-music.app/#<link token>`), so that the link token never reaches a web server or its access logs. It SHALL show the event's admission window and that each Scanner works on the first device that opens its link only, and offer a link to the staff guide, opened in a new tab, to hand to venue staff with the links.

#### Scenario: Create two scanners

- **WHEN** an operator creates two Scanners for an event without Scanners
- **THEN** `受付1` and `受付2` are listed as 未使用, each with a link to copy

#### Scenario: Link opened by staff

- **WHEN** staff open the link of `受付1` at 14:10
- **THEN** the screen shows `受付1` as 使用中 since 14:10 and no longer shows its link

### Requirement: Revoke and reissue in one step

For a Scanner that is not revoked the screen SHALL offer to revoke it, and to revoke and reissue it, which revokes the Scanner and creates a new one, showing its link. Both SHALL ask for confirmation first.

#### Scenario: Staff changed phones

- **WHEN** the operator revokes and reissues `受付1` of an event with Scanners 1 and 2, and confirms
- **THEN** `受付1` is 取り消し済み and a new 未使用 `受付3` is shown with its link

#### Scenario: Unpublished event

- **WHEN** the operator opens the screen for a DRAFT event
- **THEN** the screen says the event must be published before Scanners can be created

#### Scenario: Event without a start time

- **WHEN** the operator opens the screen for a published event without a start time
- **THEN** the screen says the event needs a start time before Scanners can be created
