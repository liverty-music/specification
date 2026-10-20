## ADDED Requirements

### Requirement: Cross-border data-transfer disclosure and retention

The platform's privacy disclosure SHALL state that personal data is entrusted to Stripe (US) as a cross-border transfer (個人情報 越境移転) and SHALL be backed by an executed DPA; payment records SHALL be retained per 電子帳簿保存法.

#### Scenario: Privacy disclosure covers the Stripe US transfer

- **WHEN** a fan reviews the privacy policy before paying
- **THEN** the Stripe (US) 越境移転 委託 is disclosed, a DPA is in place, and payment records are retained per 電子帳簿保存法

### Requirement: Terms of Service state the ticket purchase terms

The Terms of Service SHALL include a ticket purchase article stating:
- that the platform sells tickets on behalf of the Organizer, who is the business selling them (販売業者), and collects the payment as the Organizer's 収納代行 (collection agency), so that paying the platform discharges the fan's debt to the Organizer;
- that the purchase contract is concluded when the order is placed on the final confirmation screen;
- that tickets cannot be cancelled or refunded except when the event is 中止 (cancelled), when the full price of the tickets still held is refunded to the card used, and that no cooling-off applies;
- that tickets are bound to the fan's account and name and resale without the Organizer's consent is prohibited.

#### Scenario: Purchase article present
- **WHEN** the Terms of Service is displayed
- **THEN** it states the Organizer as the business selling the tickets, the platform's collection on its behalf, when the contract is concluded, and the cancellation-only refund rule
