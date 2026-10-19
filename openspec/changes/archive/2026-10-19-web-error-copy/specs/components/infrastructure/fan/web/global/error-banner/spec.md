# Spec Delta

## ADDED Requirements

### Requirement: The banner's text comes from the app's catalog

The error banner SHALL show a title, a message and its button labels from the app's own catalog in the fan's language, with the Error ID, and SHALL NOT show the captured error's message. The title SHALL be 問題が発生しました (Something went wrong) and the message SHALL be 予期しないエラーが発生しました。ページを再読み込みしてください。 (An unexpected error occurred. Reload the page.). The error's message stays in the copied error details, the report and the browser console log.

#### Scenario: Unhandled error shows fixed copy

- **WHEN** an unhandled promise rejection with the message `Cannot read properties of undefined (reading 'id')` opens the error banner for a fan using Japanese
- **THEN** the banner shows 問題が発生しました, the fixed message and the Error ID, and `Cannot read properties` appears nowhere in the banner

#### Scenario: English labels

- **WHEN** the error banner opens for a fan using English
- **THEN** the title, the message and the button labels are in English
