# Spec Delta

## Purpose

The organizer console page of one event (one date of a concert): its date, venue and publish state with the actions on it, a Sales tab for the event's TicketSales and a Reception (受付) tab for the Scanners venue staff use at the door.

## ADDED Requirements

### Requirement: The event header and its actions

The page SHALL show the event's date and start time in Japan time, its venue and its publish state as a labelled badge, and SHALL offer the actions that apply to the event's state: 公開する (publish) for a draft event, 中止する (cancel) for an event that is not cancelled, and 編集 (edit), which opens the concert editor. Publishing and cancelling SHALL ask for confirmation first, naming the effect, and on success the page SHALL show the new state and confirm it in the snackbar. A cancelled event SHALL show that it is cancelled and offer no action. The page SHALL have two tabs, 販売 (Sales) and 受付 (Reception), each with its own address so a tab can be reopened or shared; the page opens on 販売. An event of another Organizer, or one that does not exist, SHALL show that the event was not found with a link to its concert or to Concerts.

#### Scenario: Draft event

- **WHEN** an operator opens a draft event of XX Tour 2026 on 3 November at Zepp Haneda
- **THEN** the header shows 11月3日(火) 18:00 JST · Zepp Haneda with the badge 下書き and offers 公開する, 中止する and 編集

#### Scenario: Publish confirmed

- **WHEN** the operator presses 公開する and confirms in the dialog
- **THEN** the badge becomes 公開中 and the snackbar says the event was published

#### Scenario: Reception tab address

- **WHEN** an operator opens the Reception tab's address directly after signing in
- **THEN** the event page opens with 受付 selected

### Requirement: The Sales tab explains a missing prerequisite

The Sales tab SHALL say why no sale can be started, and link to where to fix it, when the event is not published (link: the event's 公開する action), has no start time (link: the concert editor), or the Organizer's business details (legal name, representative name, business address, business phone number, contact email) are not complete (no link; it says they are entered by Liverty Music during vetting and how to contact Liverty Music). While a prerequisite is missing, the tab SHALL not offer to start a sale.

#### Scenario: Draft event

- **WHEN** an operator opens the Sales tab of a draft event
- **THEN** it says 販売を始めるには、公演を公開してください with a link to publish, and no sale can be started

#### Scenario: No start time

- **WHEN** the event is published and has no start time
- **THEN** the tab says the start time must be set first and links to the concert editor

#### Scenario: Business details incomplete

- **WHEN** the event is published and timed and the Organizer has no business address
- **THEN** the tab says the business details are entered by Liverty Music during vetting, and no sale can be started

### Requirement: The Sales tab lists the event's sales by state

The Sales tab SHALL list every TicketSale that offers a TicketType for the event, in start order, each with its name, its method (抽選 lottery or 先着 first come), its window in Japan time, and its TicketType's price, quantity and per-account limit, and its verification requirement. Each sale SHALL show its state:

- scheduled (受付開始前), before the start time: the time remaining until it opens, updated at least once a minute (for example あと 2日 3時間);
- open (受付中), within the window: for a lottery, the number of entries, the number of requested tickets and the quantity, and when requested tickets exceed the quantity, the ratio as a percentage;
- closed and not drawn (抽選待ち), for a lottery after the end time before the draw;
- drawn (抽選済み), for a lottery: the number of winning entries, the number of tickets won and the number of waitlisted (Lost) entries.

When the event has no sale the tab SHALL say so and offer 抽選で販売する (sell by lottery) and 先着で販売する (sell first come). When the event has sales, the tab SHALL still offer to start another sale after them. A first-come sale shows what the first-come sale editor specifies.

#### Scenario: No sale yet

- **WHEN** a published, timed event of an Organizer with complete business details has no sale
- **THEN** the tab says この公演日の販売はまだありません and offers 抽選で販売する and 先着で販売する

#### Scenario: Scheduled lottery

- **WHEN** it is 2026-10-08 09:00 JST and a lottery sale opens on 2026-10-10 12:00 JST
- **THEN** the sale shows 受付開始前 あと 2日 3時間 with its window 10月10日(土) 12:00 〜 10月17日(土) 23:59 JST, price 6,500円 and 1,200 tickets, up to 4 per account

#### Scenario: Open lottery, oversubscribed

- **WHEN** an open lottery of 1,200 tickets has 412 entries requesting 1,380 tickets
- **THEN** the sale shows 412 entries, 1,380 requested tickets and 1,200 tickets, and says the requests are 115% of the quantity

#### Scenario: Drawn lottery

- **WHEN** a drawn lottery has 318 winning entries for 1,198 tickets and 94 Lost entries
- **THEN** the sale shows 当選 318, 1,198 tickets won and 94 waitlisted

#### Scenario: Presale drawn, general sale scheduled

- **WHEN** an event has a drawn ファンクラブ先行 and a 一般発売 that has not opened
- **THEN** both are listed, ファンクラブ先行 first, and another sale can still be started

### Requirement: Start a lottery from the Sales tab

抽選で販売する SHALL open the lottery sale editor for this event, and after the sale is created the console SHALL return to this Sales tab showing the new sale and confirm it in the snackbar.

#### Scenario: Lottery created

- **WHEN** an operator presses 抽選で販売する, fills in ファンクラブ先行 and saves
- **THEN** the Sales tab opens with ファンクラブ先行 listed as 受付開始前 or 受付中 and the snackbar confirms it

### Requirement: Change a sale's verification requirement

Each sale SHALL offer a choice of its verification requirement — 本人確認なし (None), 本人確認済み (Verified-any) or マイナンバーカードで本人確認済み (JPKI-only) — at any time, including while open and after the draw, saying that entries already made are not checked again. A change SHALL be saved when chosen; on failure the choice SHALL return to the saved value and the snackbar SHALL offer 再試行.

#### Scenario: Tighten while open

- **WHEN** an operator changes an open sale from 本人確認なし to マイナンバーカードで本人確認済み
- **THEN** the sale's requirement is JPKI-only and the snackbar confirms it

#### Scenario: Change fails

- **WHEN** the change fails because the network is down
- **THEN** the choice shows 本人確認なし again and the snackbar offers 再試行

### Requirement: The Reception tab lists one Scanner per device

The Reception tab SHALL list the event's Scanners by number, labelled 受付1, 受付2 and so on, with their state: 未使用 (Unused), 使用中 (InUse) with the time it was first opened in Japan time, or 取り消し済み (Revoked). It SHALL let the operator issue a Scanner with one action, without asking for a name, and show the new Scanner's link with actions to copy and share it; the new row SHALL enter the list with a short motion. The link SHALL be on the reception origin, which is separate from the console origin, and carry the token in its fragment, so that the token never reaches a web server or its access logs. An InUse or Revoked Scanner SHALL no longer show its link. The tab SHALL show the event's reception window and that each link works only on the first device that opens it, and offer a link to the reception guide, opened in a new tab, to hand to venue staff with the links.

#### Scenario: Issue two scanners

- **WHEN** an operator issues two Scanners for an event without Scanners
- **THEN** 受付1 and 受付2 are listed as 未使用, each with a link to copy

#### Scenario: Scanner opened by staff

- **WHEN** staff open 受付1 at 14:10 JST
- **THEN** the tab shows 受付1 as 使用中 since 14:10 JST and no longer shows its link

### Requirement: Revoke and reissue a Scanner

For a Scanner that is not Revoked the tab SHALL offer 取り消す (revoke) and 取り消して再発行 (revoke and reissue), which revokes the Scanner and issues a new one, showing its link. Both SHALL ask for confirmation first, saying the device using it stops working.

#### Scenario: Staff changed phones

- **WHEN** the operator revokes and reissues 受付1 of an event with Scanners 1 and 2, and confirms
- **THEN** 受付1 is 取り消し済み and a new 未使用 受付3 is shown with its link

### Requirement: The Reception tab explains a missing prerequisite

The Reception tab SHALL say, and not offer to issue a Scanner, when the event is not published (link: the event's 公開する action) or has no start time (link: the concert editor).

#### Scenario: Unpublished event

- **WHEN** the operator opens the Reception tab of a draft event
- **THEN** the tab says the event must be published before links can be issued

#### Scenario: Event without a start time

- **WHEN** the operator opens the Reception tab of a published event without a start time
- **THEN** the tab says the event needs a start time before links can be issued
