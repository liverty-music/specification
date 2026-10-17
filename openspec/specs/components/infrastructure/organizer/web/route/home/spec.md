# components/infrastructure/organizer/web/route/home Specification

## Purpose
The organizer console's first screen: the list of things that need the member now, each with the one action that resolves it, so a member who opens the console knows what to do without searching.

## Requirements

### Requirement: Home lists what needs the member, most urgent first

Home SHALL list, as one list grouped by kind under a heading per kind, items that each say what needs doing and are one target that opens where it is resolved, with no other action inside the item:

1. 要対応 (needs action): the Organizer's payout account is not active — labelled 登録する (set up), opening Settings at the payout account;
2. 7日以内 (within 7 days): a published event that starts within the next 7 days (Japan time) and has no Scanner that is Unused or InUse — labelled 発行する (issue), opening that event's Reception tab;
3. 開始時刻なし (no start time): a published event without a start time — labelled 設定する (set), opening the concert editor of its concert;
4. 下書き (draft): a concert that has a draft event — opening that concert's page.

Items SHALL be ordered by this list and, within a kind, by event date, earliest first. A cancelled event or concert SHALL never appear. An item about a concert SHALL open it under the first of its performers that the Organizer represents.

#### Scenario: Payout account not finished

- **WHEN** the Organizer's payout account is pending
- **THEN** Home shows 入金口座の登録が終わっていません labelled 登録する, first in the list

#### Scenario: Event next week without a scanner

- **WHEN** it is 2026-10-28 and a published event starts on 2026-11-03 18:00 JST and has no Scanner
- **THEN** Home shows 11月3日(火) 18:00 JST · 受付リンクなし labelled 発行する, and selecting the item opens that event's Reception tab

#### Scenario: Revoked scanners only

- **WHEN** the same event's only Scanner is Revoked
- **THEN** the item is still shown

#### Scenario: Published event without a start time

- **WHEN** a published event of XX Tour 2026 on 2026-12-20 has no start time
- **THEN** Home shows the event labelled 設定する, and selecting it opens the concert editor of XX Tour 2026

#### Scenario: Draft concert

- **WHEN** XX 単独公演 has a draft event on 2026-12-20
- **THEN** Home shows XX 単独公演 · 12月20日(日) under 下書き, and selecting it opens the concert page

### Requirement: Nothing to do is said plainly

When no item applies, Home SHALL say that nothing needs attention and offer a link to Concerts. When one of the sources cannot be read, Home SHALL show the items it could read, say which part could not be loaded, and offer 再試行 (retry) for that part.

#### Scenario: All clear

- **WHEN** the payout account is active and no event or concert matches an item
- **THEN** Home says nothing needs attention and links to Concerts

#### Scenario: Payout status unavailable

- **WHEN** the payout account cannot be read but the concerts can
- **THEN** Home shows the concert items and says the payout status could not be loaded, with 再試行
