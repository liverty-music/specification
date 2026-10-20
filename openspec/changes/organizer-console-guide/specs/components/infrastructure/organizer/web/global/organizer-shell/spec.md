## MODIFIED Requirements

### Requirement: Persistent navigation around every screen

Every console screen except sign-in and access denied SHALL be shown inside a frame with three destinations — ホーム (Home), 公演 (Concerts) and 設定 (Settings) — with the current destination marked, the names Liverty Music and Organizer Console (in English in every language; no other or shortened product name), the Organizer's name, the represented Artist being worked on (a menu to change it when the Organizer represents two or more Artists), a help action 使い方 (Help) that opens the members' guide, and an account menu holding the language switch and サインアウト (sign out). Signing out SHALL end the session and show the sign-in page. Every screen SHALL belong to one destination: Home to ホーム; Concerts, a concert, the concert editor, an event and the sale editors to 公演; Settings to 設定. 公演 SHALL open the concerts of the Artist being worked on: the Artist in the current address, else the Artist last opened on this device, else the first represented Artist by name.

#### Scenario: Sign out from any screen

- **WHEN** a member on an event page opens the account menu and chooses サインアウト
- **THEN** the session ends and the sign-in page is shown, and the back button does not reopen the event page signed in

#### Scenario: Current destination on a deep page

- **WHEN** a member is on the Sales tab of an event
- **THEN** 公演 is marked as the current destination

#### Scenario: Product name in Japanese

- **WHEN** the console is shown in Japanese
- **THEN** the top of the frame reads Liverty Music and Organizer Console, and no other product name appears

#### Scenario: Change the Artist

- **WHEN** the Organizer XX Records represents Band A and Band B, a member works on Band A and chooses Band B from the Artist menu
- **THEN** the concerts of Band B are shown and 公演 opens them from now on

## ADDED Requirements

### Requirement: Help opens the guide at the current screen's chapter

The help action SHALL be an icon in the top bar next to the account menu, named 使い方 in Japanese and Help in English for screen readers and shown as a tooltip, on every screen inside the frame and at every window width. It SHALL open the members' guide in a new browser tab, so the console keeps its state, including unsaved input in an editor, at the chapter for the current screen:

| screen | chapter |
|---|---|
| Home | ホームの見かた |
| Concerts, a concert, the concert editor | 公演をつくって公開する |
| an event's Sales tab, the lottery and first-come sale editors | チケットを販売する |
| an event's Reception tab | 受付リンクを発行する |
| Settings | 事業者情報と受取口座 |

The guide SHALL be in Japanese whatever language the console is set to.

#### Scenario: Help on the Sales tab

- **WHEN** a member on the Sales tab of an event selects 使い方
- **THEN** the guide opens in a new tab at the chapter チケットを販売する, and the Sales tab stays open in the console's tab

#### Scenario: Help while editing

- **WHEN** a member who has typed a title in the concert editor without saving selects 使い方
- **THEN** the guide opens in a new tab at 公演をつくって公開する, no unsaved-changes dialog appears, and the typed title is still in the editor

#### Scenario: Help on a phone

- **WHEN** a member opens an event page in a 390 px wide window
- **THEN** the top bar shows the back arrow, the page title, 使い方 and the account menu, none of them overlapping

#### Scenario: Console in English

- **WHEN** the console is in English and a member selects Help on Settings
- **THEN** the guide opens in Japanese at the chapter 事業者情報と受取口座
