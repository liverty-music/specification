## MODIFIED Requirements

### Requirement: Home lists what needs the member, most urgent first

Home SHALL list, as one list grouped by kind under a heading per kind, items that each say what needs doing and are one target that opens where it is resolved, with no other action inside the item:

1. 要対応 (needs action): the Organizer has no payout account yet, or its payout account is not active — labelled 登録する (set up), opening Settings at the payout account;
2. 7日以内 (within 7 days): a published event that starts within the next 7 days (Japan time) and has no Scanner that is Unused or InUse — labelled 発行する (issue), opening that event's Reception tab;
3. 開始時刻なし (no start time): a published event without a start time — labelled 設定する (set), opening the concert editor of its concert;
4. 下書き (draft): a concert that has a draft event — opening that concert's page.

Items SHALL be ordered by this list and, within a kind, by event date, earliest first. A cancelled event or concert SHALL never appear. An item about a concert SHALL open it under the first of its performers that the Organizer represents. An Organizer that has no payout account yet is a state Home shows as the 要対応 item, never as a payout status that could not be loaded.

#### Scenario: Payout account not finished

- **WHEN** the Organizer's payout account is pending
- **THEN** Home shows 入金口座の登録が終わっていません labelled 登録する, first in the list

#### Scenario: No payout account yet

- **WHEN** the Organizer has no payout account
- **THEN** Home shows 入金口座の登録が終わっていません labelled 登録する, first in the list, selecting it opens Settings at the payout account, and Home does not say the payout status could not be loaded

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
