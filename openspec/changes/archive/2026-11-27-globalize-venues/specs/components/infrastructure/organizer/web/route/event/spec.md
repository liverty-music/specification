## MODIFIED Requirements

### Requirement: The event header and its actions

The page SHALL show the event's date and start time at its Venue's local time, labelled with the Venue's time zone and, for a zone other than Asia/Tokyo, the Japan time (global/i18n "Dates and times in the zone they belong to"), its venue and its publish state as a labelled badge, and SHALL offer the actions that apply to the event's state: 公開する (publish) for a draft event, which publishes this date only, as the page's main action, and, in a menu of further actions, 中止する (cancel) for an event that is not cancelled and 公演を編集 (edit the concert), which opens the concert editor. Publishing and cancelling SHALL ask for confirmation first, naming the effect (for a draft date, that 中止する removes it); the publish confirmation SHALL say that publishing this date alone notifies followers for this date, and point to the concert page to publish several dates with one notification, and on success the page SHALL show the new state and confirm it in the snackbar. When the publish is refused with FailedPrecondition, the snackbar SHALL say that the date's venue, date and start time are already used by another concert or by a cancelled date and that the member changes the date or start time in the concert editor, SHALL offer no retry, and the page SHALL show the event's current state. A cancelled event SHALL show that it is cancelled and offer no action. The page SHALL have two tabs, 販売 (Sales) and 受付 (Reception), each with its own address so a tab can be reopened or shared; the page opens on 販売. An event of another Organizer, or one that does not exist, SHALL show that the event was not found with a link to its concert or to Concerts.

#### Scenario: Draft event

- **WHEN** a member opens a draft event of XX Tour 2026 on 3 November at Zepp Haneda
- **THEN** the header shows 11月3日(火) 18:00 日本時間 · Zepp Haneda with the badge 下書き and offers 公開する, with 中止する and 公演を編集 in its menu

#### Scenario: Event abroad

- **WHEN** a member opens an event of XX Tour 2027 that starts on 2027-02-20 at 19:30 at a Venue in London
- **THEN** the header shows 2月20日(土) 19:30 ロンドン時間（日本時間 2月21日(日) 04:30） with the venue

#### Scenario: Publish confirmed

- **WHEN** the member presses 公開する and confirms in the dialog
- **THEN** the badge becomes 公開中 and the snackbar says the event was published

#### Scenario: Publish refused for a used slot

- **WHEN** the member publishes a draft event on 11 December 18:00 at Zepp Haneda, and another concert of the Organizer already has a date there
- **THEN** the snackbar says the venue, date and start time are already used and to change the date or start time in the concert editor, no retry is offered, and the badge stays 下書き

#### Scenario: Reception tab address

- **WHEN** a member opens the Reception tab's address directly after signing in
- **THEN** the event page opens with 受付 selected

### Requirement: The Sales tab lists the event's sales by state

The Sales tab SHALL list every TicketSale that names the event, in start order, each with its name, its method (抽選 lottery or 先着 first come), its window in the sale's time zone labelled with that zone's name, and its verification requirement, and SHALL say once, above the list, that every sale sells the event's seat types in 席種と枚数 and that one account may hold up to the event's per-account limit across all sales, with that limit. Each sale SHALL show its state:

- scheduled (受付開始前), before the start time: the time remaining until it opens, updated at least once a minute (for example あと 2日 3時間);
- open (受付中), within the window: for a lottery, for each seat type, the number of entries, the number of requested tickets and the remaining tickets of its TicketStock, and when requested tickets exceed the remaining tickets, the ratio as a percentage;
- closed and not drawn (抽選待ち), for a lottery after the end time before the draw;
- drawn (抽選済み), for a lottery: the number of winning entries, the number of tickets won and the number of losers (Lost entries);
- ended (販売終了), for a first-come sale after the end time.

The sold and held tickets of a first-come sale are shown per seat type in 席種と枚数.

When the event has no sale the tab SHALL say so and offer 抽選で販売する (sell by lottery) and 先着で販売する (sell first come). When the event has sales, the tab SHALL still offer to start another lottery after them, and SHALL offer 先着で販売する only while the event has no first-come sale.

#### Scenario: No sale yet

- **WHEN** a published, timed event with a TicketStock, of an Organizer with complete business details, has no sale
- **THEN** the tab says この公演日の販売はまだありません and offers 抽選で販売する and 先着で販売する

#### Scenario: Scheduled lottery

- **WHEN** it is 2026-10-08 09:00 Japan time and a lottery sale in the time zone Asia/Tokyo opens on 2026-10-10 12:00
- **THEN** the sale shows 受付開始前 あと 2日 3時間 with its window 10月10日(土) 12:00 〜 10月17日(土) 23:59 日本時間

#### Scenario: Sale in another zone

- **WHEN** a lottery sale in the time zone Asia/Seoul opens on 2027-02-01 12:00 and closes on 2027-02-10 23:59
- **THEN** the sale's window is shown as 2月1日(月) 12:00 〜 2月10日(水) 23:59 ソウル時間

#### Scenario: Open lottery, oversubscribed

- **WHEN** an open lottery has 412 entries requesting 1,380 S席 tickets and S席 has 1,200 tickets remaining
- **THEN** the sale shows for S席 412 entries, 1,380 requested tickets and 1,200 remaining, and says the requests are 115% of the remaining tickets

#### Scenario: Drawn lottery

- **WHEN** a drawn lottery has 318 winning entries for 1,198 tickets and 94 Lost entries
- **THEN** the sale shows 当選 318, 1,198 tickets won and 94 losers

#### Scenario: First-come sale on sale

- **WHEN** a first-come sale is open and S席 of 150 has 100 sold and 6 held
- **THEN** the sale shows 受付中, and 席種と枚数 shows S席 with 100 sold, 6 held and 150 tickets

#### Scenario: Presale drawn, general sale scheduled

- **WHEN** an event has a drawn ファンクラブ先行 and a 一般発売 that has not opened
- **THEN** both are listed, ファンクラブ先行 first, and another sale can still be started

### Requirement: The Reception tab lists one Scanner per device

The Reception tab SHALL list the event's Scanners by number, labelled 受付1, 受付2 and so on, with their state: 未使用 (Unused), 使用中 (InUse) with the time it was first opened in the time zone of the event's Venue, labelled with that zone's name, or 取り消し済み (Revoked). It SHALL let the member issue a Scanner with one action, without asking for a name, and show the new Scanner's link with actions to copy and share it; the new row SHALL enter the list with a short motion. The link SHALL be on the reception origin, which is separate from the console origin, and carry the token in its fragment, so that the token never reaches a web server or its access logs. An InUse or Revoked Scanner SHALL no longer show its link. The tab SHALL show the event's reception window and that each link works only on the first device that opens it, and offer a link to the reception guide, opened in a new tab, to hand to venue staff with the links.

#### Scenario: Issue two scanners

- **WHEN** a member issues two Scanners for an event without Scanners
- **THEN** 受付1 and 受付2 are listed as 未使用, each with a link to copy

#### Scenario: Scanner opened by staff

- **WHEN** staff open 受付1 of an event at a Venue in Tokyo at 14:10 Japan time
- **THEN** the tab shows 受付1 as 使用中 since 14:10 日本時間 and no longer shows its link

#### Scenario: Scanner opened abroad

- **WHEN** staff open 受付1 of an event at a Venue in London at 17:40 London time, and the member's device is set to Japan time
- **THEN** the tab shows 受付1 as 使用中 since 17:40 ロンドン時間
