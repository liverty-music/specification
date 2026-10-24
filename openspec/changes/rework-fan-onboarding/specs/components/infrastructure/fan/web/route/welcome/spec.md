## ADDED Requirements

### Requirement: Analytics notice under the Get Started button

The Welcome page SHALL show an analytics notice directly under every Get Started button it renders: under the hero button when no preview is shown, and under the button in the demo footer. The notice SHALL be two lines:

- 「使いやすさの改善のため、利用状況を分析しています。分析に名前やメールアドレスは使いません。」
- 「いつでもオフにできます ・ 詳しく」, where 「オフにできます」 opens the analytics opt-out on the Settings screen and 「詳しく」 opens the analytics details page, which names the recipient, the data sent and the purpose and links the privacy policy.

The notice SHALL NOT name the analytics provider; the details page does. The first line SHALL wrap only at phrase boundaries, never inside a word. The notice SHALL be visible to every visitor on every visit, SHALL need no acknowledgement and SHALL NOT block the Get Started button. The English locale SHALL show an equivalent text.

#### Scenario: Notice under the demo footer button

- **WHEN** a visitor scrolls to the demo footer
- **THEN** the two notice lines SHALL appear directly under the Get Started button

#### Scenario: Notice under the hero button without a preview

- **WHEN** the Welcome page renders without the preview, so Get Started is in the hero
- **THEN** the two notice lines SHALL appear directly under that button

#### Scenario: Turning analytics off from the notice

- **WHEN** the visitor taps 「オフにできます」
- **THEN** the Settings screen SHALL open at the analytics opt-out

#### Scenario: Reading the details

- **WHEN** the visitor taps 「詳しく」
- **THEN** the analytics details page SHALL open, naming the recipient, the data sent and the purpose, with a link to the privacy policy

#### Scenario: Phrase-boundary wrapping on a narrow screen

- **WHEN** the Welcome page renders 360 px wide in Japanese
- **THEN** the first notice line SHALL break only between phrases
