# components/infrastructure/organizer/web/route/guide Specification

## Purpose
The members' guide to the organizer console: a static page, opened from the console without sign-in, that explains each thing a member does in the console in the order they do it, with the console's own words.

## Requirements

### Requirement: A page anyone with the address can read

The guide SHALL open at an address on the organizer console's origin without asking for a sign-in, SHALL show no data of any Organizer, and SHALL be in Japanese whatever language the console is set to. It SHALL be readable without horizontal scrolling in a 390 px wide window and in a 1280 px wide window, in the browsers the console supports.

#### Scenario: Opened signed out

- **WHEN** a person who is not signed in opens the guide's address
- **THEN** the guide is shown and no sign-in starts

#### Scenario: Opened on a phone

- **WHEN** a member opens the guide in a 390 px wide window
- **THEN** every chapter is readable without scrolling sideways

### Requirement: Chapters follow what a member wants to do

The guide SHALL have one chapter for each of these, in this order: ホームの見かた (reading Home), サインインする (signing in, on the usual device and on a new device), 事業者情報と受取口座 (business details and the payout account), 公演をつくって公開する (creating and publishing a concert), 公開した公演を変える (correcting a published concert, adding a date, 中止 cancelling), チケットを販売する (selling by lottery and first come), 売れ行きと紹介コード (sales progress and referral codes) and 受付リンクを発行する (issuing reception links, and what to do when a device cannot be used at the door). It SHALL begin with a list of the chapters, each a link to its chapter, and each chapter SHALL have its own address, so that a link to that address opens the guide at that chapter.

#### Scenario: Contents

- **WHEN** a member opens the guide
- **THEN** the list of chapters is at the top, in the order above, and selecting チケットを販売する scrolls to that chapter

#### Scenario: Link to a chapter

- **WHEN** a member opens the address of the chapter 受付リンクを発行する
- **THEN** the guide opens with that chapter at the top of the window

### Requirement: A map of the console's screens

After the list of chapters, the guide SHALL show a map of the console: the three destinations ホーム, 公演 and 設定; under 公演 the concert list, a concert, the concert editor, an event with its 販売 (Sales) and 受付 (Reception) tabs, and the sale editors; and which screen each kind of Home item opens.

#### Scenario: Where a Home item leads

- **WHEN** a member looks up the 7日以内 item of Home on the map
- **THEN** the map shows that it opens the Reception tab of the event

### Requirement: The console's words, as the console shows them

Every button, tab, state, heading and notice of the console that the guide names SHALL read exactly as the Japanese console shows it, so that a member can find it on the screen by its words.

#### Scenario: Publishing step

- **WHEN** a member reads how to publish a concert
- **THEN** the guide names the buttons 公開する and 公演を中止 and the states as the console shows them

#### Scenario: Selling step

- **WHEN** a member reads how to start a sale
- **THEN** the guide names 抽選で販売する, 先着で販売する and the sale states 受付開始前, 受付中, 抽選待ち and 抽選済み as the console shows them

### Requirement: What the screens do not say

The guide SHALL explain what a member cannot learn from the console's screens alone:

- a referral code is chosen by the member, not registered in the console: the member adds `?ref=<code>` to the address of a date's fan event page and shares that address; a paid purchase counts under the code when the fan bought within 7 days of opening that address, and under the last code the fan opened;
- the business details (特商法 表記, the commercial transactions disclosure) are entered by Liverty Music during vetting, sales cannot start until every detail is registered, and changes are asked of the member's contact at Liverty Music;
- on a new device the member reaches their Organizer's sign-in either through the console's address with `?org=<the Organizer's short name>` or by entering their email on the console's first screen and opening the link that is emailed;
- a lottery is drawn automatically shortly after its window closes, and nothing about it can change once its window has opened.

#### Scenario: Referral link

- **WHEN** a member reads the chapter 売れ行きと紹介コード
- **THEN** it shows an example address of a fan event page with `?ref=` and a code, and says how long and for which code a purchase counts

#### Scenario: Sale blocked by business details

- **WHEN** a member reads the chapter 事業者情報と受取口座
- **THEN** it says that Liverty Music registers the business details and that sales cannot start until they are complete
