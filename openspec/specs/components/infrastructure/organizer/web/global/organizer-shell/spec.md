# Organizer Shell

## Purpose

The organizer frontend shell: a dedicated `organizer.html` entry,
bundle-isolated from the consumer SPA and admin console, authenticated
against the operator's own Zitadel tenant org via org-pinned entry, with a
role-claim route guard and a post-login placeholder. Business screens land
in later changes.

## Requirements

### Requirement: Only owner-role operators enter, and they land on Home

The organizer console SHALL guard its screens: an unauthenticated visitor is sent to sign-in for the Organization the console knows (see "Without a known Organization the console asks for the email" for a console that knows none), and an authenticated user is admitted only if the token's `organizer-console` project roles include `owner`; otherwise the console shows a page saying access is denied, with a sign-out action. The backend remains the source of truth for authorization; the guard is a gate for the screens. An admitted operator SHALL land on the Home of their own Organizer, and an address the console does not know SHALL open that Home.

#### Scenario: Unauthenticated visitor goes to sign-in

- **WHEN** an unauthenticated visitor opens any console address on a device that remembers their Organizer's Organization, or with the Organization in the address
- **THEN** they are sent to sign-in for that Organization, and after signing in they return to the address they opened

#### Scenario: Owner lands on Home

- **WHEN** an authenticated operator whose token carries the `owner` role opens the console
- **THEN** the Home of the operator's Organizer is shown, at an address that names that Organizer

#### Scenario: Account without the owner role

- **WHEN** an authenticated user whose token lacks the `owner` role opens the console
- **THEN** the access denied page is shown with a sign-out action, and no console screen opens

#### Scenario: Old or unknown address

- **WHEN** an operator opens `lottery/status/abc`, `/concerts` or any other address the console does not know
- **THEN** the Home of the operator's Organizer is shown

### Requirement: Persistent navigation around every screen

Every console screen except sign-in and access denied SHALL be shown inside a frame with three destinations — ホーム (Home), 公演 (Concerts) and 設定 (Settings) — with the current destination marked, the names Liverty Music and Organizer Console (in English in every language; no other or shortened product name), the Organizer's name, the represented Artist being worked on (a menu to change it when the Organizer represents two or more Artists), and an account menu holding the language switch and サインアウト (sign out). Signing out SHALL end the session and show the sign-in page. Every screen SHALL belong to one destination: Home to ホーム; Concerts, a concert, the concert editor, an event and the sale editors to 公演; Settings to 設定. 公演 SHALL open the concerts of the Artist being worked on: the Artist in the current address, else the Artist last opened on this device, else the first represented Artist by name.

#### Scenario: Sign out from any screen

- **WHEN** an operator on an event page opens the account menu and chooses サインアウト
- **THEN** the session ends and the sign-in page is shown, and the back button does not reopen the event page signed in

#### Scenario: Current destination on a deep page

- **WHEN** an operator is on the Sales tab of an event
- **THEN** 公演 is marked as the current destination

#### Scenario: Product name in Japanese

- **WHEN** the console is shown in Japanese
- **THEN** the top of the frame reads Liverty Music and Organizer Console, and no other product name appears

#### Scenario: Change the Artist

- **WHEN** the Organizer XX Records represents Band A and Band B, an operator works on Band A and chooses Band B from the Artist menu
- **THEN** the concerts of Band B are shown and 公演 opens them from now on

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

Every screen below a destination SHALL show a breadcrumb of its parents up to the destination (for example 公演 › XX Tour 2026 › 11月3日(火)), each part a link except the current page. In a window narrower than 600 px the breadcrumb SHALL be replaced by a back arrow in the top bar that leads to the parent. Every screen SHALL be reachable by navigation from its destination: a concert from Concerts, an event from its concert, a sale editor from its event's Sales tab.

#### Scenario: Breadcrumb on an event

- **WHEN** an operator opens the event of 3 November of XX Tour 2026
- **THEN** the breadcrumb reads 公演 › XX Tour 2026 › 11月3日(火), and 公演 and XX Tour 2026 are links

#### Scenario: Breadcrumb on a phone

- **WHEN** the same page is opened in a 390 px wide window
- **THEN** a back arrow in the top bar leads back to XX Tour 2026

#### Scenario: Every screen reached by navigation

- **WHEN** an operator starts at Home
- **THEN** they can reach any concert, event, Sales tab, Reception tab, sale editor and Settings by selecting links, without typing an address

### Requirement: Addresses name the Organizer and the Artist

Every console address below sign-in SHALL start with the operator's Organizer (`/organizers/<organizer id>`), and every address of the 公演 destination SHALL continue with a represented Artist (`/artists/<artist id>/series/...`), so a copied address opens the same screen for any operator of the same Organizer. A concert SHALL open under each represented Artist who performs in it, and SHALL be not found under any other Artist. An address naming another Organizer SHALL show that the address belongs to another Organizer, with サインアウト to switch accounts, and SHALL show none of its data; the backend stays the source of truth for what the operator may read.

#### Scenario: Copied address

- **WHEN** an operator copies the address of the Sales tab of the 3 November event of XX Tour 2026 and another operator of the same Organizer opens it
- **THEN** the same Sales tab opens

#### Scenario: Co-headlined concert

- **WHEN** Band A and Band B, both represented by XX Records, perform in XX × YY 2026
- **THEN** the concert is listed in the concerts of each, opens under either Artist's address, and its breadcrumb follows the Artist in the address

#### Scenario: Another Organizer's address

- **WHEN** an operator of XX Records opens an address that names another Organizer
- **THEN** the page says the address belongs to another Organizer and offers サインアウト, and no console screen opens

#### Scenario: No represented Artist yet

- **WHEN** an operator of an Organizer that represents no Artist selects 公演
- **THEN** the page says no Artist is represented yet and that Liverty Music adds Artists on request

### Requirement: Without a known Organization the console asks for the email

When an unauthenticated visitor opens any console address and the console knows no Organization - none in the address and none remembered on the device - the console SHALL open the find-organizer screen instead of starting a sign-in, and SHALL return the visitor to the address they opened once they sign in through a link. When the console knows an Organization, the guard sends the visitor to sign-in for that Organization as before.

#### Scenario: New device

- **WHEN** an organizer opens `https://organizer.liverty-music.app/` on a new phone
- **THEN** the find-organizer screen is shown and no sign-in starts

#### Scenario: Remembered Organization

- **WHEN** the organizer opens the console on a device where they signed in before
- **THEN** the sign-in for their Organizer's Organization starts

#### Scenario: Return after a link sign-in

- **WHEN** an organizer on a new phone opens a console address, is shown the find-organizer screen and then signs in through the link in the email within 24 hours
- **THEN** the address they first opened is shown
