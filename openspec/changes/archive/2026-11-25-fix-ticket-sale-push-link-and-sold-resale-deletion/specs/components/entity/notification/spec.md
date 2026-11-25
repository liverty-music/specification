## MODIFIED Requirements

### Requirement: The link and the grouping tag follow the type

A Notification's link SHALL be: for new_concerts, ticket_sale_announcement, sales_reminder, lottery_loss and concert_cancelled, which are about a concert (the earliest matched concert for new_concerts, the fan's linked event or the event otherwise), `/concerts/<id>` when the concert's Series is first-party and `/timetable?concert=<id>` otherwise, because a discovered concert has no concert page; for lottery_win and resale_win, the Tickets screen; for resale_entry_lapsed and resale_entry_lost, the resale entry screen; for order_refunded, the Order. Its grouping tag SHALL be one per artist for new_concerts, one per TicketSale for ticket_sale_announcement, one per TicketSale and stage for sales_reminder, and one per type and subject otherwise, so a later message with the same tag replaces the earlier one on a device. The link and the tag do not depend on the language.

#### Scenario: Two reminder stages
- **WHEN** a TicketSale's `APPLY_OPEN` and `APPLY_CLOSE_24H` reminders are rendered for one fan
- **THEN** their tags differ

#### Scenario: Same artist again
- **WHEN** two new_concerts Notifications are rendered for the same artist
- **THEN** their tags are the same

#### Scenario: Ticket sale push for a discovered concert

- **WHEN** a ticket_sale_announcement or a sales_reminder Notification is rendered for a TicketSale whose linked event's Series is not first-party
- **THEN** its link is `/timetable?concert=<id>` of that event

#### Scenario: Ticket sale push for a first-party concert

- **WHEN** a ticket_sale_announcement or a sales_reminder Notification is rendered for a TicketSale whose linked event's Series is first-party
- **THEN** its link is `/concerts/<id>` of that event

