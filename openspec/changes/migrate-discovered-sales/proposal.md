## Why

After `unify-ticket-sales` and `first-come-ticket-sales`, one sale (受付) is modelled twice: the Organizer's `TicketSale` and the discovered `SalesPhase`. Both are a Series-level sale with a method and a window, but only the discovered one has reminders. A fan who tracks an Organizer's tour is never reminded when its lottery opens, closes or announces results. Moving discovered sales into `TicketSale` gives one sale model and lets the same reminders cover the Organizer's own sales.

## What Changes

- **Discovered sales become `TicketSale`s.** A discovered sale is a TicketSale of a Series without an Organizer. It offers no TicketType and has a discovered time. It has no name and no verification requirement, and it is never drawn. Nothing new marks a sale as the Organizer's or as discovered: the sale's Series tells. Discovery now searches only Series without an Organizer. Today it can also search an Organizer's Series, because only the concert search skips represented artists.
- **`TicketSale` accepts discovered data.** The name, the 1-to-14-day lottery window and the required end time apply only to an Organizer's sale. A discovered FirstCome sale may have no end time. A discovered Lottery sale may have a lottery result time (当落発表, result announcement).
- **A lottery has a result time.** It is the lottery result time when the sale has one. For an Organizer's Lottery sale it is the end time, because the draw runs within 1 minute after the end time.
- **The Organizer's sales get reminders too (new behavior).** Fans get the open, closing-in-24-hours and result-day reminders for the Organizer's sales as well as for discovered sales, while the Series is Published. For a discovered sale the audience stays every fan tracking an event of the Series. For an Organizer's sale it is the fans tracking an event the sale offers, because such a sale can cover only some events of the tour. Only discovered sales are announced when they appear, as today.
- **BREAKING** `SalesPhase` is removed. Its operations move onto `TicketSale`: `UpsertDiscovered`, `ListBySeries`, `ListWithPendingMilestones` and `SearchPublishedSales`. `SalesMethod` is merged into `TicketSaleMethod` (Lottery, FirstCome).
- **BREAKING** `SalesPhaseReminder` → `TicketSaleReminder` and `SalesPhaseSearchLog` → `TicketSaleSearchLog`, with the same rules.
- **BREAKING** The usecases are renamed. `SalesPhaseDiscoveryUseCase.DiscoverForArtist` → `TicketSaleDiscoveryUseCase.DiscoverForArtist`. `SalesPhaseAnnouncementUseCase.AnnounceDiscoveredPhase` → `TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale`. `SalesReminderUseCase.ScanDueReminders` → `TicketSaleReminderUseCase.ScanDueReminders`. `SalesReminderDeliveryUseCase.DeliverReminder` → `TicketSaleReminderDeliveryUseCase.DeliverReminder`.
- The notification type `sales_phase_announcement` becomes `ticket_sale_announcement`.
- The lottery draw skips discovered sales. A discovered Lottery sale closes like any lottery, but the platform has nothing to draw.
- Production data moves: every stored sales phase becomes a discovered sale with the same id, and the stored reminder records and search logs come with it.

Fans see the same notifications for discovered sales as before. No fan screen shows a discovered sale today, and none starts to.

## Capabilities

### New Capabilities

- `components/entity/ticket-sale-reminder`: the record that one reminder stage of one TicketSale was sent to one User; the stages and their anchors
- `components/entity/ticket-sale-reminder/already-sent`, `list-sent-stages`, `record-sent`: the operations of `SalesPhaseReminder`, keyed by TicketSale
- `components/entity/ticket-sale-search-log`: when a Series was last searched for published ticket sales
- `components/entity/ticket-sale-search-log/list-by-series`, `record`: the operations of `SalesPhaseSearchLog`
- `components/entity/ticket-sale/upsert-discovered`: stores a discovered sale, converging on series, method and start date in Japan time
- `components/entity/ticket-sale/list-by-series`: every sale of one Series
- `components/entity/ticket-sale/list-with-pending-milestones`: the sales, discovered or the Organizer's, that may have a reminder to act on
- `components/entity/ticket-journey/list-user-ids-tracking-events`: the fans tracking any of the given events, each with a linked event among them; the audience of an Organizer's sale
- `components/entity/ticket-sale/search-published-sales`: the search of the artist's official pages for sales that have not opened
- `components/usecase/ticket-sale/discover-for-artist`: the daily discovery, storing discovered TicketSales and searching only Series without an Organizer
- `components/usecase/ticket-sale/announce-discovered-sale`: the announcement of a newly discovered sale to tracking fans
- `components/usecase/ticket-sale/scan-due-reminders`: the 15-minute reminder scan over discovered and Organizer's sales
- `components/usecase/ticket-sale-reminder/deliver-reminder`: delivery of one due reminder

### Modified Capabilities

- `components/entity/ticket-sale` (created by `unify-ticket-sales`): "A lottery window lasts 1 to 14 days" and "A sale has a name" are scoped to an Organizer's sale. Added: the two kinds of sale, required times by method and kind, the result time, the discovered time, and when a sale is not yet over. (Purpose) `name` and `end time` become optional for a discovered sale. The rows `lottery result time` and `discovered time` are added. Method is Lottery or FirstCome. The diagram changes to `TicketSale ||--o{ TicketType` and adds `TicketSale ||--o{ TicketSaleReminder`.
- `components/entity/ticket-sale/list-due-for-draw` (created by `unify-ticket-sales`): "Sales due for draw" returns only an Organizer's sales.
- `components/usecase/notification/deliver`: "Runs for each requested notification" names `TicketSaleAnnouncementUseCase.AnnounceDiscoveredSale`.
- `components/entity/user/delete`: "Delete removes the user and what it owns" names ticket sale reminder records.
- `components/entity/concert/delete-and-suppress`: "Delete and suppress together" keeps the Series' TicketSales.
- `stories/get-reminded-of-ticket-sale-milestones`: "Milestone reminders by method reach tracking fans" covers every TicketSale of the Series and the renamed usecases. Added: "The Organizer's own sales are reminded too", for fans tracking an event the sale offers.
- `stories/hear-about-a-new-ticket-sale`: requirements renamed from "sales phase" to "discovered sale", with the renamed usecases and notification type. (Purpose) "a new ticket sales phase" → "a new discovered ticket sale".
- `components/entity/series` (Purpose): diagram `Series ||--o{ SalesPhase` → `Series ||--o{ TicketSale`.
- `components/entity/notification` (Purpose): type value `sales_phase_announcement` → `ticket_sale_announcement`, and the sentence's "sales-phase announcement" becomes "ticket sale announcement".
- `components/entity/ticket-journey/list-user-ids-tracking-series` (Purpose): "ticket sales phases" → "ticket sales".

Entity operations the usecases rely on and this change does not alter: `TicketJourney.ListUserIDsTrackingSeries`, `Follow.ListAll`, `Concert.ListByArtist`, `Artist` official site read, `Series.Get`, `User.Get`, `NotificationUseCase.Deliver` (its caller list only), `TicketSale.Create`, `TicketSale.ListByEvent` (a discovered sale offers no TicketType, so it never matches an event).

### Removed Capabilities

These are written as REMOVED deltas:
- `components/entity/sales-phase` and its operations `get-by-series`, `list-phases-with-pending-milestones`, `search-sales-phases`, `upsert`
- `components/entity/sales-phase-reminder` and its operations `already-sent`, `list-sent-stages`, `record-sent`
- `components/entity/sales-phase-search-log` and its operations `list-by-series`, `record`
- `components/usecase/sales-phase/announce-discovered-phase`, `discover-for-artist`, `scan-due-reminders`
- `components/usecase/sales-phase-reminder/deliver-reminder`

## Impact

- **specification**: `entity/v1/sales_phase.proto` is deleted (`SalesPhase`, `SalesPhaseId`, `SalesMethod`). No RPC and no client uses it. This is a breaking change on BSR, released with the `buf skip breaking` label. `TicketSale` in `ticket_sale.proto` is unchanged, because no RPC returns a discovered sale. Its doc comment says so.
- **backend**:
  - One Atlas migration: `ticket_sales` gains `lottery_result_at` and `discovered_at`, and `name` and `end_at` become nullable for discovered rows. Every `sales_phases` row is copied with its id. `sales_phase_reminders` → `ticket_sale_reminders`, `sales_phase_search_logs` → `ticket_sale_search_logs`. `sales_phases` is dropped. Stored notification types are rewritten.
  - The discovery, announcement, reminder-scan and delivery code moves onto `TicketSale`. The Gemini searcher returns discovered sales. The draw query excludes discovered sales.
- **frontend**: none. No screen shows a discovered sale, and the generated clients drop an unused type.
- **cloud-provisioning**: none required. The NATS stream `SALES_PHASE`, its subjects, the CronJob `sales-phase-discovery` and the log-based metric keep their names (design.md "Non-Goals").
- **Production data**: `sales_phases`, `sales_phase_reminders` and `sales_phase_search_logs` hold real discovered data. They are read before the migration, read-only, and checked after it.
- **Sequencing**: lands after `unify-ticket-sales` and `first-come-ticket-sales` archive. This change's MODIFIED deltas copy their text.
