# Spec Delta

## MODIFIED Requirements

### Requirement: Chapters follow what a member wants to do

The guide SHALL have one chapter for each of these, in this order: ホームの見かた (reading Home), サインインする (signing in, on the usual device and on a new device), 事業者情報と受取口座 (business details and the payout account), 公演をつくって公開する (creating and publishing a concert), 公開した公演を変える (correcting a published concert, adding a date, 中止 cancelling), チケットを販売する (setting the concert's seat types, each date's quantities and per-account limit, and selling by lottery and first come), 売れ行きと紹介コード (sales progress and referral codes) and 受付リンクを発行する (issuing reception links, and what to do when a device cannot be used at the door). It SHALL begin with a list of the chapters, each a link to its chapter, and each chapter SHALL have its own address, so that a link to that address opens the guide at that chapter.

#### Scenario: Contents

- **WHEN** a member opens the guide
- **THEN** the list of chapters is at the top, in the order above, and selecting チケットを販売する scrolls to that chapter

#### Scenario: Link to a chapter

- **WHEN** a member opens the address of the chapter 受付リンクを発行する
- **THEN** the guide opens with that chapter at the top of the window

### Requirement: What the screens do not say

The guide SHALL explain what a member cannot learn from the console's screens alone:

- a referral code is chosen by the member, not registered in the console: the member adds `?ref=<code>` to the address of a date's fan event page and shares that address; a paid purchase counts under the code when the fan bought within 7 days of opening that address, and under the last code the fan opened;
- the business details (特商法 表記, the commercial transactions disclosure) are entered by Liverty Music during vetting, sales cannot start until every detail is registered, and changes are asked of the member's contact at Liverty Music;
- on a new device the member reaches their Organizer's sign-in either through the console's address with `?org=<the Organizer's short name>` or by entering their email on the console's first screen and opening the link that is emailed;
- a lottery is drawn automatically shortly after its window closes, and nothing about it can change once its window has opened;
- every sale of a date sells all of that date's seat types from the same quantities, so a presale can sell every ticket and leave nothing for a later sale;
- a seat type's name and price, and a date's quantity of it, never change once saved; more tickets are released as another seat type, such as 注釈付き指定席;
- one account holds tickets of only one seat type per date, up to the date's per-account limit across all sales.

#### Scenario: Referral link

- **WHEN** a member reads the chapter 売れ行きと紹介コード
- **THEN** it shows an example address of a fan event page with `?ref=` and a code, and says how long and for which code a purchase counts

#### Scenario: Sale blocked by business details

- **WHEN** a member reads the chapter 事業者情報と受取口座
- **THEN** it says that Liverty Music registers the business details and that sales cannot start until they are complete

#### Scenario: Shared quantities

- **WHEN** a member reads the chapter チケットを販売する
- **THEN** it says that every sale of a date sells from the same quantities, that quantities and prices never change, and that more tickets are released as another seat type
