## ADDED Requirements

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
