## MODIFIED Requirements

### Requirement: Consent toggles invite the fan to help, in plain words

The Settings page SHALL present the analytics consent toggles using labels and descriptions that name the consent *purpose* (what the data is used for) in words a fan without technical knowledge understands, and that invite the fan to help improve the service. They SHALL NOT name the data's processing *geography*, and SHALL NOT call the data anonymous, because a signed-in fan's data is tied to their account. The onboarding consent notice SHALL follow the same rule: its introduction SHALL be true for a guest and for a signed-in fan, so it SHALL NOT call the analytics anonymous and SHALL say that they are linked to the account while the fan is signed in. Each consent toggle on the Settings page SHALL remain a persistent, user-controlled opt-out for the corresponding consent purpose. The Settings page SHALL NOT present a per-region ("domestic" vs "overseas") processing toggle, and SHALL NOT remove a consent purpose's Settings opt-out while that purpose can be granted at signup.

In Japanese the section and toggles SHALL read:

- Section 「サービス改善の協力」, introduced by 「Liverty Music はユーザーの皆さんと共に進化していきます。あなたの使い方が、次のアップデートを決める一番の手がかりになります。」
- Analytics: label 「利用状況を共有する」, description 「どの画面で迷ったか、どこでエラーが起きたかを知って、改善に役立てます。名前・メールアドレス・電話番号などは送りません。オフにすると、利用状況とエラーの情報を送らなくなります。」
- Session replay: label 「画面操作ログを共有する」, description 「タップやスクロールの流れを、入力内容や画面の文字を伏せて記録します。わかりにくいボタンや迷いやすい手順を見つけるために使います。オフにしても、他の設定には影響しません。」

#### Scenario: Analytics toggle is labeled by its purpose

- **WHEN** the サービス改善の協力 section is rendered
- **THEN** the product-analytics toggle SHALL be bound to the product-analytics consent purpose
- **AND** its label SHALL read 「利用状況を共有する」 in Japanese
- **AND** its description SHALL say that it is used to find where fans get lost and where errors occur, that name, email address and phone number are not sent, and what turning it off stops

#### Scenario: Session-replay toggle is labeled by its purpose

- **WHEN** the サービス改善の協力 section is rendered
- **THEN** the second toggle SHALL be bound to the `sessionReplay` consent purpose
- **AND** its label SHALL read 「画面操作ログを共有する」 in Japanese
- **AND** its description SHALL say that typed input and on-screen text are hidden in the recording, and that turning it off has no effect on other settings

#### Scenario: No anonymity claim

- **WHEN** either consent toggle's description is shown, in any language
- **THEN** it SHALL NOT describe the data as anonymous or anonymised

#### Scenario: Consent notice makes no anonymity claim

- **WHEN** the onboarding consent notice's introduction is shown, in any language
- **THEN** it SHALL NOT describe the data as anonymous or anonymised
- **AND** it SHALL say that the analytics are linked to the account while the fan is signed in

#### Scenario: Settings opt-out persists for a purpose granted at signup

- **WHEN** a user granted a consent purpose at the signup consent screen
- **THEN** the Settings page SHALL render a corresponding toggle that lets the user withdraw that consent
- **AND** the toggle SHALL reflect the persisted consent state on load
