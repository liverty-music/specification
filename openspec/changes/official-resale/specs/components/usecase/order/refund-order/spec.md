## ADDED Requirements

### Requirement: Seller refund triggered on resale completion

The system SHALL refund the seller **their own original payment minus the resale
fee**, **triggered at the atomic match** (the resale completing), **NOT held to
the event**. The net settlement to the seller SHALL carry a **hold-back reserve —
a fixed window measured from the match** (a dispute buffer; ~days to ~3 weeks, the
exact length a tunable operational parameter) — after which it releases; it MUST
NOT be tied to the event occurring. If the seller's original
payment method can no longer be reversed at settlement time (e.g. an expired card),
the system SHALL fall back to an alternative payout (e.g. bank transfer).

#### Scenario: Refund triggered when the resale completes

- **WHEN** a resale match completes
- **THEN** the seller's refund (original payment minus the resale fee) is triggered, subject to a short hold-back reserve, without waiting for the event

#### Scenario: Chargeback handled via hold-back, not event-gating

- **WHEN** a buyer charges back a resold seat
- **THEN** the platform draws on the hold-back reserve and represents the dispute with the delivered-ticket / entry evidence, clawing back via reversal if needed

#### Scenario: Refund falls back when the card cannot be reversed

- **WHEN** the seller's original card is expired or closed at settlement time
- **THEN** the system pays the seller via an alternative payout method instead of a card reversal

### Requirement: Resale fee

The system SHALL charge the **seller** a **single resale fee as a percentage of
face value** (default ~10%, business-configurable), and SHALL charge it **only on
a successful resale**. If a listing does not sell, the system MUST NOT charge any
fee. The fee SHALL be defined in the terms as **consideration for a service
rendered (役務提供の対価** — matching / payment / 本人確認), not a cancellation
penalty (違約金). Fee computation SHALL apply a **defined rounding rule** and, when
the seller's refundable original amount is less than the computed fee, SHALL
**clamp the fee to the refundable amount** (never producing a negative payout). The
fee and per-Organizer 事業者情報 SHALL be disclosed on the confirmation screen
(特定商取引法に基づく表記).

#### Scenario: Fee charged only on success

- **WHEN** a listing sells
- **THEN** the seller's refund is reduced by the resale fee and the fee terms were disclosed before listing

#### Scenario: No fee when unsold

- **WHEN** a listing does not sell by the deadline
- **THEN** no resale fee is charged

#### Scenario: Fee is clamped to the refundable amount

- **WHEN** the computed fee would exceed the seller's refundable original amount
- **THEN** the fee is clamped so the seller payout is never negative
