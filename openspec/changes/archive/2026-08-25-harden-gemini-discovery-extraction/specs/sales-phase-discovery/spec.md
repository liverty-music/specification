# sales-phase-discovery Specification (delta)

## ADDED Requirements

### Requirement: Play-guide sales are classified as プレイガイド even when general

When a sales phase is conducted through a named third-party play guide (for example e+ / イープラス, ローチケ, チケットぴあ, CN Playguide), the grounded extraction step SHALL classify its channel as `プレイガイド` and record the guide in `provider_name`, even when the sale is a general (non-membership) on-sale. The `一般` channel SHALL be reserved for a general on-sale that is not tied to a named play guide.

#### Scenario: General on-sale sold via a named play guide
- **WHEN** a general on-sale for a series is sold through イープラス
- **THEN** the phase channel SHALL be `プレイガイド`
- **AND** `provider_name` SHALL be the guide name (e.g. `イープラス`)
- **AND** the channel SHALL NOT be `一般`

#### Scenario: General on-sale with no named guide
- **WHEN** a general on-sale is a direct sale on the official site with no third-party play guide named
- **THEN** the phase channel SHALL be `一般`

### Requirement: Lottery phases extract the application deadline and result date when published

For a `抽選` (lottery) phase, the grounded extraction step SHALL extract the application deadline (`apply_end`) and the result-announcement date (`lottery_result`) from the ticket page when they are published alongside the application window, and SHALL leave them empty only when they are genuinely absent — never guessed.

#### Scenario: Lottery with a published deadline and result date
- **WHEN** a `抽選` phase's page publishes an application window with a deadline and a result-announcement date
- **THEN** the extracted phase SHALL include both `apply_end` and `lottery_result`

#### Scenario: Lottery with no published result date
- **WHEN** a `抽選` phase's page does not publish a result-announcement date
- **THEN** `lottery_result` SHALL be left empty rather than guessed
