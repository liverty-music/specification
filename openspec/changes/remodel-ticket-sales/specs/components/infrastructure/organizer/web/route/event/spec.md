# Spec Delta

## ADDED Requirements

### Requirement: The Sales tab sets the event's seat types and quantities

The Sales tab SHALL show a section 席種と枚数 (seat types and quantities) listing the event's TicketStocks, read with TicketStockService.ListByEvent, each with its seat type's name and price 税込 (tax-inclusive), its quantity, its sold count and its held count, and its state: 販売可 (Available), 残りは購入手続き中 (AllHeld) or 完売 (SoldOut). It SHALL offer 席種を追加 (add a seat type), which asks for one of the concert's seat types not yet stocked for the event and a quantity of at least 1, and creates the TicketStock with TicketStockService.Create after a confirmation saying that the quantity cannot be changed afterwards and that every sale of the event sells it. A TicketStock with no Order SHALL offer 削除 (delete), which deletes it with TicketStockService.Delete after confirmation; one with an Order SHALL offer no delete. When the concert has no seat type, the section SHALL say to add seat types on the concert page and link to it. The section SHALL be shown whatever the event's prerequisites for selling.

#### Scenario: Two seat types stocked

- **WHEN** a member adds S席 with 300 tickets and A席 with 700 tickets to the 3 November event
- **THEN** the section lists S席 8,000円 300枚 and A席 6,000円 700枚, both 販売可 with nothing sold or held

#### Scenario: More tickets later

- **WHEN** S席 is SoldOut and the member wants to release 20 more tickets
- **THEN** the section offers no way to raise S席's quantity, and the member adds another seat type of the concert, such as 注釈付き指定席, with 20 tickets

#### Scenario: Stock already ordered

- **WHEN** a fan has an Order for S席 of the event
- **THEN** S席 offers no delete

#### Scenario: Concert without seat types

- **WHEN** the event's concert has no seat type
- **THEN** the section says to add seat types on the concert page and links to it

## MODIFIED Requirements

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
