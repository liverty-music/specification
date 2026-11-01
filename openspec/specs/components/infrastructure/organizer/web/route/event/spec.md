# components/infrastructure/organizer/web/route/event Specification

## Purpose
The organizer console page of one event (one date of a concert): its date, venue and publish state with the actions on it, a Sales tab for the event's TicketSales and its purchases per referral code, and a Reception (受付) tab for the Scanners venue staff use at the door.

## Requirements

### Requirement: The event header and its actions

The page SHALL show the event's date and start time in Japan time, its venue and its publish state as a labelled badge, and SHALL offer the actions that apply to the event's state: 公開する (publish) for a draft event, which publishes this date only, as the page's main action, and, in a menu of further actions, 中止する (cancel) for an event that is not cancelled and 公演を編集 (edit the concert), which opens the concert editor. Publishing and cancelling SHALL ask for confirmation first, naming the effect (for a draft date, that 中止する removes it); the publish confirmation SHALL say that publishing this date alone notifies followers for this date, and point to the concert page to publish several dates with one notification, and on success the page SHALL show the new state and confirm it in the snackbar. When the publish is refused with FailedPrecondition, the snackbar SHALL say that the date's venue, date and start time are already used by another concert or by a cancelled date and that the member changes the date or start time in the concert editor, SHALL offer no retry, and the page SHALL show the event's current state. A cancelled event SHALL show that it is cancelled and offer no action. The page SHALL have two tabs, 販売 (Sales) and 受付 (Reception), each with its own address so a tab can be reopened or shared; the page opens on 販売. An event of another Organizer, or one that does not exist, SHALL show that the event was not found with a link to its concert or to Concerts.

#### Scenario: Draft event

- **WHEN** a member opens a draft event of XX Tour 2026 on 3 November at Zepp Haneda
- **THEN** the header shows 11月3日(火) 18:00 JST · Zepp Haneda with the badge 下書き and offers 公開する, with 中止する and 公演を編集 in its menu

#### Scenario: Publish confirmed

- **WHEN** the member presses 公開する and confirms in the dialog
- **THEN** the badge becomes 公開中 and the snackbar says the event was published

#### Scenario: Publish refused for a used slot

- **WHEN** the member publishes a draft event on 11 December 18:00 at Zepp Haneda, and another concert of the Organizer already has a date there
- **THEN** the snackbar says the venue, date and start time are already used and to change the date or start time in the concert editor, no retry is offered, and the badge stays 下書き

#### Scenario: Reception tab address

- **WHEN** a member opens the Reception tab's address directly after signing in
- **THEN** the event page opens with 受付 selected

### Requirement: The fan page of a published date

For a published date of a PUBLIC concert, the page SHALL show the address of the date's fan event page (`/events/<event id>` on the fan app) with a copy action, so the member can share it. A draft or cancelled date, and any date of an UNLISTED concert, SHALL show no fan address, because fans cannot open it.

#### Scenario: Public date

- **WHEN** a member opens the published 3 November event of the PUBLIC concert XX Tour 2026
- **THEN** the page shows the fan page address of that event, and copying puts it on the clipboard

#### Scenario: Unlisted concert

- **WHEN** a member opens a published event of an UNLISTED concert
- **THEN** no fan page address is shown

### Requirement: The Sales tab explains a missing prerequisite

The Sales tab SHALL say why no sale can be started, and link to where to fix it, when the event is not published (link: the event's 公開する action), has no start time (link: the concert editor), has no TicketStock (pointing to the section 席種と枚数 on the same tab), or the Organizer's business details (legal name, representative name, business address, business phone number, contact email) are not complete (no link to a fix; it says they are entered by Liverty Music during vetting and how to contact Liverty Music). Each of these notices SHALL also link to the members' guide, opened in a new tab, at the chapter that explains it: 公演をつくって公開する for an unpublished event or a missing start time, チケットを販売する for a missing TicketStock, and 事業者情報と受取口座 for incomplete business details. While a prerequisite is missing, the tab SHALL not offer to start a sale.

#### Scenario: Draft event

- **WHEN** a member opens the Sales tab of a draft event
- **THEN** it says 販売を始めるには、公演を公開してください with a link to publish and a link to the guide's chapter 公演をつくって公開する, and no sale can be started

#### Scenario: No start time

- **WHEN** the event is published and has no start time
- **THEN** the tab says the start time must be set first and links to the concert editor and to the guide's chapter 公演をつくって公開する

#### Scenario: No seat type stocked

- **WHEN** the event is published and timed and has no TicketStock
- **THEN** the tab says to add seat types and quantities in 席種と枚数 first, links to the guide's chapter チケットを販売する, and no sale can be started

#### Scenario: Business details incomplete

- **WHEN** the event is published and timed and the Organizer has no business address
- **THEN** the tab says the business details are entered by Liverty Music during vetting, links to the guide's chapter 事業者情報と受取口座, and no sale can be started

### Requirement: The Sales tab lists the event's sales by state

The Sales tab SHALL list every TicketSale that names the event, in start order, each with its name, its method (抽選 lottery or 先着 first come), its window in Japan time and its verification requirement, and SHALL say once, above the list, that every sale sells the event's seat types in 席種と枚数 and that one account may hold up to the event's per-account limit across all sales, with that limit. Each sale SHALL show its state:

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

- **WHEN** it is 2026-10-08 09:00 JST and a lottery sale opens on 2026-10-10 12:00 JST
- **THEN** the sale shows 受付開始前 あと 2日 3時間 with its window 10月10日(土) 12:00 〜 10月17日(土) 23:59 JST

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

### Requirement: Start a lottery from the Sales tab

抽選で販売する SHALL open the lottery sale editor for this event, and after the sale is created the console SHALL return to this Sales tab showing the new sale and confirm it in the snackbar.

#### Scenario: Lottery created

- **WHEN** a member presses 抽選で販売する, fills in ファンクラブ先行 and saves
- **THEN** the Sales tab opens with ファンクラブ先行 listed as 受付開始前 or 受付中 and the snackbar confirms it

### Requirement: Edit a sale from the Sales tab

Each first-come sale SHALL offer 編集, which opens the first-come sale editor for the event. Each lottery sale SHALL offer 編集 before its start time, which opens the lottery sale editor for that sale; from its start time on, 編集 SHALL be shown disabled with 受付開始後は変更できません.

#### Scenario: Edit a first-come sale

- **WHEN** a member presses 編集 on the 一般発売 first-come sale
- **THEN** the first-come sale editor opens for the event with that sale's name and window

#### Scenario: Edit a lottery before it opens

- **WHEN** a member presses 編集 on a lottery sale that opens tomorrow
- **THEN** the lottery sale editor opens with that sale's name and window

#### Scenario: Lottery already open

- **WHEN** a lottery sale's window has opened
- **THEN** its 編集 is disabled and says 受付開始後は変更できません

### Requirement: Change a sale's verification requirement

Each sale SHALL offer a choice of its verification requirement — 本人確認なし (None), 本人確認済み (Verified-any) or マイナンバーカードで本人確認済み (JPKI-only) — at any time, including while open and after the draw, saying that entries already made are not checked again. A change SHALL be saved when chosen; on failure the choice SHALL return to the saved value and the snackbar SHALL offer 再試行.

#### Scenario: Tighten while open

- **WHEN** a member changes an open sale from 本人確認なし to マイナンバーカードで本人確認済み
- **THEN** the sale's requirement is JPKI-only and the snackbar confirms it

#### Scenario: Change fails

- **WHEN** the change fails because the network is down
- **THEN** the choice shows 本人確認なし again and the snackbar offers 再試行

### Requirement: The Reception tab lists one Scanner per device

The Reception tab SHALL list the event's Scanners by number, labelled 受付1, 受付2 and so on, with their state: 未使用 (Unused), 使用中 (InUse) with the time it was first opened in Japan time, or 取り消し済み (Revoked). It SHALL let the member issue a Scanner with one action, without asking for a name, and show the new Scanner's link with actions to copy and share it; the new row SHALL enter the list with a short motion. The link SHALL be on the reception origin, which is separate from the console origin, and carry the token in its fragment, so that the token never reaches a web server or its access logs. An InUse or Revoked Scanner SHALL no longer show its link. The tab SHALL show the event's reception window and that each link works only on the first device that opens it, and offer a link to the reception guide, opened in a new tab, to hand to venue staff with the links.

#### Scenario: Issue two scanners

- **WHEN** a member issues two Scanners for an event without Scanners
- **THEN** 受付1 and 受付2 are listed as 未使用, each with a link to copy

#### Scenario: Scanner opened by staff

- **WHEN** staff open 受付1 at 14:10 JST
- **THEN** the tab shows 受付1 as 使用中 since 14:10 JST and no longer shows its link

### Requirement: Revoke and reissue a Scanner

For a Scanner that is not Revoked the tab SHALL offer 取り消す (revoke) and 取り消して再発行 (revoke and reissue), which revokes the Scanner and issues a new one, showing its link. Both SHALL ask for confirmation first, saying the device using it stops working.

#### Scenario: Staff changed phones

- **WHEN** the member revokes and reissues 受付1 of an event with Scanners 1 and 2, and confirms
- **THEN** 受付1 is 取り消し済み and a new 未使用 受付3 is shown with its link

### Requirement: The Reception tab explains a missing prerequisite

The Reception tab SHALL say, and not offer to issue a Scanner, when the event is not published (link: the event's 公開する action) or has no start time (link: the concert editor). Each of these notices SHALL also link to the members' guide, opened in a new tab, at the chapter 公演をつくって公開する.

#### Scenario: Unpublished event

- **WHEN** the member opens the Reception tab of a draft event
- **THEN** the tab says the event must be published before links can be issued, with a link to the guide's chapter 公演をつくって公開する

#### Scenario: Event without a start time

- **WHEN** the member opens the Reception tab of a published event without a start time
- **THEN** the tab says the event needs a start time before links can be issued, with a link to the guide's chapter 公演をつくって公開する

### Requirement: The Sales tab shows purchases per referral code

When the event has at least one sale, the Sales tab SHALL show, below the sales, a section 紹介コード別の購入 (purchases per referral code) read with organizer TicketSaleService.ListByEvent. It SHALL have one row per referral code with the code as given, the number of Paid Orders (件), the number of tickets (枚) and the amount paid in yen 税込 (tax-inclusive), in the order returned (most Orders first), and one row 直接（コードなし） (direct, no code) for purchases without a code, shown last. It SHALL say that only paid purchases are counted, that refunded purchases are not counted, and that a lottery entry is counted once it won and was charged. When the event has no Paid Order, the section SHALL say まだ購入はありません (no purchases yet). The section SHALL be read-only: codes are not registered, edited or removed in the console.

#### Scenario: Two codes and direct purchases
- **WHEN** an event's Paid Orders are 12 for 21 tickets and 136,500 yen with `member-a`, 5 for 8 tickets and 52,000 yen with `member-b`, and 40 for 71 tickets and 461,500 yen without a code
- **THEN** the section lists member-a 12件 21枚 136,500円, member-b 5件 8枚 52,000円, and last 直接（コードなし） 40件 71枚 461,500円

#### Scenario: Sale with no purchase yet
- **WHEN** the event has a sale and no Paid Order
- **THEN** the section says まだ購入はありません

#### Scenario: Event without a sale
- **WHEN** the event has no sale
- **THEN** the section is not shown

### Requirement: The Sales tab sets the event's seat types and quantities

The Sales tab SHALL show a section 席種と枚数 (seat types and quantities) listing the event's TicketStocks, read with TicketStockService.ListByEvent, each with its seat type's name and price 税込 (tax-inclusive), its quantity, its sold count and its held count, and its state: 販売可 (Available), 残りは購入手続き中 (AllHeld) or 完売 (SoldOut). It SHALL offer 席種を追加 (add a seat type), which asks for one of the concert's seat types not yet stocked for the event and a quantity of at least 1, and creates the TicketStock with TicketStockService.Create after a confirmation saying that the quantity cannot be changed afterwards and that every sale of the event sells it. A TicketStock whose sold and held counts are 0 SHALL offer 削除 (delete), which deletes it with TicketStockService.Delete after confirmation, and SHALL show the refusal when a live Order still names it; one with tickets sold or held SHALL offer no delete. When the concert has no seat type, the section SHALL say to add seat types on the concert page and link to it. The section SHALL be shown whatever the event's prerequisites for selling.

#### Scenario: Two seat types stocked

- **WHEN** a member adds S席 with 300 tickets and A席 with 700 tickets to the 3 November event
- **THEN** the section lists S席 8,000円 300枚 and A席 6,000円 700枚, both 販売可 with nothing sold or held

#### Scenario: More tickets later

- **WHEN** S席 is SoldOut and the member wants to release 20 more tickets
- **THEN** the section offers no way to raise S席's quantity, and the member adds another seat type of the concert, such as 注釈付き指定席, with 20 tickets

#### Scenario: Stock already ordered

- **WHEN** a fan has bought or holds tickets of S席 of the event
- **THEN** S席 offers no delete

#### Scenario: Concert without seat types

- **WHEN** the event's concert has no seat type
- **THEN** the section says to add seat types on the concert page and links to it
