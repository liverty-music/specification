# Spec Delta

## Purpose

How every fan app screen reports a failure to the fan: with copy from the app's own catalog in the fan's language, chosen from the error code and the operation that failed, never with the server's, the payment form's or a library's error text.

## ADDED Requirements

### Requirement: A failure shows copy the app owns

When a call or an action on any fan app screen fails, the screen SHALL show copy from the app's own catalog in the fan's language, chosen from the error code and the operation that failed, in the snackbar, in the screen's inline error or next to the form that sent it. It SHALL NOT show the error message the server sent, the message the card payment form returns, or the text of an error raised in the browser. A card payment failure SHALL be told apart only by its kind (the card details are incomplete or invalid, the card was declined or could not be authenticated, anything else). An error code the screen has no copy for, and a failure that carries no error code, SHALL show the screen's copy for that operation failing. The app SHALL record the failure, with the original message, in the browser console log.

#### Scenario: Timetable fails to load

- **WHEN** loading the dashboard's timetable fails with Unavailable and the message `upstream connect error or disconnect/reset before headers`
- **THEN** the inline error says ライブの読み込みに失敗しました with a retry button, and the server's message appears nowhere on the screen

#### Scenario: Card declined at checkout

- **WHEN** authorizing the card at checkout fails because the card issuer declined it, and the card payment form returns the message `Your card has insufficient funds.`
- **THEN** the checkout says カードを利用できませんでした。 (The card could not be used.) followed by its hint that another card can be tried, and the payment form's message is not shown

#### Scenario: Card details incomplete

- **WHEN** the fan continues at checkout with an incomplete card number and the card payment form returns its own message
- **THEN** the checkout says カード情報を確認してください。 (Check the card details.) and not the payment form's message

### Requirement: A failed sign-in shows fixed copy

When completing sign-in fails and the fan has no session, the sign-in callback page SHALL show サインインできませんでした。ホームに戻って、もう一度お試しください。 (Could not sign in. Return home and try again.) and a link home, in the fan's language, and SHALL NOT show the error's own text.

#### Scenario: Sign-in callback fails

- **WHEN** completing sign-in fails with the error `No matching state found in storage` and the fan has no session
- **THEN** the page shows サインインできませんでした。ホームに戻って、もう一度お試しください。 and the link home, and the error's text is not shown
