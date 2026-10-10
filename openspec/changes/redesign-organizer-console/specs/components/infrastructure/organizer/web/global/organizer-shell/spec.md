# Spec Delta

## ADDED Requirements

### Requirement: Only owner-role operators enter, and they land on Home

The organizer console SHALL guard its screens: an unauthenticated visitor is sent to sign-in, and an authenticated user is admitted only if the token's `organizer-console` project roles include `owner`; otherwise the console shows a page saying access is denied, with a sign-out action. The backend remains the source of truth for authorization; the guard is a gate for the screens. An admitted operator SHALL land on Home, and an address the console does not know SHALL open Home.

#### Scenario: Unauthenticated visitor goes to sign-in

- **WHEN** an unauthenticated visitor opens any console address
- **THEN** they are sent to sign-in, and after signing in they return to the address they opened

#### Scenario: Owner lands on Home

- **WHEN** an authenticated operator whose token carries the `owner` role opens the console
- **THEN** Home is shown

#### Scenario: Account without the owner role

- **WHEN** an authenticated user whose token lacks the `owner` role opens the console
- **THEN** the access denied page is shown with a sign-out action, and no console screen opens

#### Scenario: Old or unknown address

- **WHEN** an operator opens `lottery/status/abc` or any other address the console does not know
- **THEN** Home is shown

### Requirement: Persistent navigation around every screen

Every console screen except sign-in and access denied SHALL be shown inside a frame with three destinations — ホーム (Home), 公演 (Concerts) and 設定 (Settings) — with the current destination marked, a top bar with the Liverty Organizer logo and the Organizer's name, and an account menu holding the language switch and サインアウト (sign out). Signing out SHALL end the session and show the sign-in page. Every screen SHALL belong to one destination: Home to ホーム; Concerts, a concert, the concert editor, an event and the sale editors to 公演; Settings to 設定.

#### Scenario: Sign out from any screen

- **WHEN** an operator on an event page opens the account menu and chooses サインアウト
- **THEN** the session ends and the sign-in page is shown, and the back button does not reopen the event page signed in

#### Scenario: Current destination on a deep page

- **WHEN** an operator is on the Sales tab of an event
- **THEN** 公演 is marked as the current destination

### Requirement: Navigation bar on a phone, navigation rail from 600 px

When the window is narrower than 600 px the destinations SHALL be shown in a navigation bar at the bottom of the window with an icon and a label each. When the window is 600 px wide or wider they SHALL be shown in a navigation rail along the left edge, with an icon and a label each. The layout SHALL change as soon as the window crosses 600 px, without a reload, and no page content SHALL be hidden behind the bar or the rail.

#### Scenario: Phone

- **WHEN** the console is opened in a 390 px wide window
- **THEN** ホーム, 公演 and 設定 are in a bar at the bottom

#### Scenario: PC

- **WHEN** the console is opened in a 1280 px wide window
- **THEN** ホーム, 公演 and 設定 are in a rail on the left and there is no bottom bar

#### Scenario: Window resized

- **WHEN** an operator narrows a 1024 px window to 560 px
- **THEN** the rail is replaced by the bottom bar and the page keeps its content and scroll position

### Requirement: No screen is reachable only by its address

Every screen below a destination SHALL show a breadcrumb of its parents up to the destination (for example 公演 › XX Tour 2026 › 11月3日(火)), each part a link except the current page. In a window narrower than 600 px the breadcrumb SHALL collapse to one link back to the parent. Every screen SHALL be reachable by navigation from its destination: a concert from Concerts, an event from its concert, a sale editor from its event's Sales tab.

#### Scenario: Breadcrumb on an event

- **WHEN** an operator opens the event of 3 November of XX Tour 2026
- **THEN** the breadcrumb reads 公演 › XX Tour 2026 › 11月3日(火), and 公演 and XX Tour 2026 are links

#### Scenario: Breadcrumb on a phone

- **WHEN** the same page is opened in a 390 px wide window
- **THEN** a single link ‹ XX Tour 2026 leads back to the concert

#### Scenario: Every screen reached by navigation

- **WHEN** an operator starts at Home
- **THEN** they can reach any concert, event, Sales tab, Reception tab, sale editor and Settings by selecting links, without typing an address

## REMOVED Requirements

### Requirement: Route guard admits only owner-role operators

**Reason**: The post-login welcome placeholder is gone; the guard now lands operators on Home and also covers unknown addresses.
**Migration**: Replaced by "Only owner-role operators enter, and they land on Home" in this spec; the role and sign-in rules are unchanged.
