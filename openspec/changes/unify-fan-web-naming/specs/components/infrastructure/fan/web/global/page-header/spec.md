# Spec Delta

## MODIFIED Requirements

### Requirement: Page identity follows the displayed route

The page header title and the active bottom-nav tab SHALL always describe the
route that is displayed. Both SHALL be taken from that route's own
configuration, so there is one source of page identity for the whole app and
no second copy of it to keep in step. They SHALL change when a navigation
completes. A navigation that fails or is cancelled leaves the previous route
displayed, and its identity SHALL remain on screen unchanged.

#### Scenario: Header title and active tab match the route shown

- **WHEN** the fan taps a bottom-nav tab and the target route is displayed
- **THEN** the page header SHALL show that route's title
- **AND** the bottom-nav highlight SHALL be on that route's tab

#### Scenario: A failed navigation leaves identity unchanged

- **WHEN** a navigation fails or is cancelled and the previous route remains
  displayed
- **THEN** the page header title and the active tab SHALL still be those of the
  previous route
- **AND** at no point SHALL they have shown the failed target

#### Scenario: Redirects and the fallback route are reflected

- **WHEN** a navigation resolves to a different route than the one requested
  (a redirect, or the not-found fallback)
- **THEN** the page header title and the active tab SHALL be those of the route
  actually displayed

#### Scenario: Routes without a page header

- **WHEN** the displayed route is one that shows no page header (welcome, About,
  the concert page, consent, the legal documents, the sign-in, passkeys and
  identity verification callbacks, not-found)
- **THEN** no page header SHALL be rendered
- **AND** the browser tab SHALL still show the route's title

## ADDED Requirements

### Requirement: A screen has one English title

Each fan screen SHALL have one title: its navigation tab label or its screen title in the brand expression registry (`components/infrastructure/fan/web/global/i18n`), in English in every language the app offers. The page header, where the screen has one, and the browser tab SHALL both show that title. A Discovery view or a sheet opened on a screen SHALL NOT change the screen's title.

#### Scenario: Japanese display keeps the English title
- **WHEN** a fan using the app in Japanese opens checkout
- **THEN** the page header and the browser tab both show "Checkout"

#### Scenario: A sheet does not change the title
- **WHEN** a fan opens `/timetable?concert=<id>`
- **THEN** the browser tab shows "Timetable"
