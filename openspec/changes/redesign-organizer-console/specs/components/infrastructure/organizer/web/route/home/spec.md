# Spec Delta

## Purpose

The organizer console's first screen: the list of things that need the operator now, each with the one action that resolves it, so an operator who opens the console knows what to do without searching.

## ADDED Requirements

### Requirement: Home lists what needs the operator, most urgent first

Home SHALL list, as one list of items each with a short reason and one action link:

1. 要対応 (needs action): the Organizer's payout account is not active — action 登録する (set up), which opens Settings at the payout account;
2. 7日以内 (within 7 days): a published event that starts within the next 7 days (Japan time) and has no Scanner that is Unused or InUse — action 発行する (issue), which opens that event's Reception tab;
3. 開始時刻なし (no start time): a published event without a start time — action 設定する (set), which opens the concert editor of its concert;
4. 下書き (draft): a concert that has a draft event — action 開く (open), which opens that concert's page.

Items SHALL be ordered by this list and, within a kind, by event date, earliest first. A cancelled event or concert SHALL never appear.

#### Scenario: Payout account not finished

- **WHEN** the Organizer's payout account is pending
- **THEN** Home shows 入金口座の登録が終わっていません with 登録する first in the list

#### Scenario: Event next week without a scanner

- **WHEN** it is 2026-10-28 and a published event starts on 2026-11-03 18:00 JST and has no Scanner
- **THEN** Home shows 11月3日(火) 18:00 JST · 受付リンクなし with 発行する, which opens that event's Reception tab

#### Scenario: Revoked scanners only

- **WHEN** the same event's only Scanner is Revoked
- **THEN** the item is still shown

#### Scenario: Published event without a start time

- **WHEN** a published event of XX Tour 2026 on 2026-12-20 has no start time
- **THEN** Home shows the event with 設定する, which opens the concert editor of XX Tour 2026

#### Scenario: Draft concert

- **WHEN** XX 単独公演 has a draft event on 2026-12-20
- **THEN** Home shows 下書き XX 単独公演 · 12月20日(日) with 開く

### Requirement: Nothing to do is said plainly

When no item applies, Home SHALL say that nothing needs attention and offer a link to Concerts. When one of the sources cannot be read, Home SHALL show the items it could read, say which part could not be loaded, and offer 再試行 (retry) for that part.

#### Scenario: All clear

- **WHEN** the payout account is active and no event or concert matches an item
- **THEN** Home says nothing needs attention and links to Concerts

#### Scenario: Payout status unavailable

- **WHEN** the payout account cannot be read but the concerts can
- **THEN** Home shows the concert items and says the payout status could not be loaded, with 再試行
