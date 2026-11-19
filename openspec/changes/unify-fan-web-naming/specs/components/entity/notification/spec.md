# Spec Delta

## MODIFIED Requirements

### Requirement: The link and the grouping tag follow the type

A Notification's link SHALL be: for new_concerts, `/concerts/<id>` of the earliest matched concert when its Series is first-party and `/timetable?concert=<id>` otherwise; for ticket_sale_announcement and sales_reminder, the concert page of the fan's linked event; for lottery_win and resale_win, the Tickets screen; for lottery_loss and concert_cancelled, the event's page; for resale_entry_lapsed and resale_entry_lost, the resale entry screen; for order_refunded, the Order. Its grouping tag SHALL be one per artist for new_concerts, one per TicketSale for ticket_sale_announcement, one per TicketSale and stage for sales_reminder, and one per type and subject otherwise, so a later message with the same tag replaces the earlier one on a device. The link and the tag do not depend on the language.

#### Scenario: Two reminder stages
- **WHEN** a TicketSale's `APPLY_OPEN` and `APPLY_CLOSE_24H` reminders are rendered for one fan
- **THEN** their tags differ

#### Scenario: Same artist again
- **WHEN** two new_concerts Notifications are rendered for the same artist
- **THEN** their tags are the same
