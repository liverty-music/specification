# Spec Delta

## ADDED Requirements

### Requirement: A screen has one English title

Each fan screen SHALL have one title, written in English in every language the app offers, and the page header and the browser tab SHALL both show that title. A screen without a page header SHALL still show its title in the browser tab. The titles are:

| screen | title |
|---|---|
| timetable | Timetable |
| concert | Concert |
| discovery | Discovery |
| my-artists | My Artists |
| tickets | Tickets |
| notifications | Notifications |
| settings | Settings |
| passkeys | Passkeys |
| delete-account | Delete Account |
| order | Order Detail |
| checkout | Checkout |
| new-lottery-entry | Lottery Entry |
| lottery-entries | Lottery Entries |
| new-resale-entry | Resale Entry |
| resale-entries | Resale Entries |
| sign-in-help | Can't Sign In |
| verify-email | Verify Email |
| welcome | Welcome |
| about | About |
| consent | Privacy & Analytics |
| legal (terms) | Terms of Service |
| legal (privacy) | Privacy Policy |
| legal (licenses) | OSS Licenses |

A Timetable tab, a Discovery view or a sheet opened on a screen SHALL NOT change the screen's title.

#### Scenario: Japanese display keeps the English title
- **WHEN** a fan using the app in Japanese opens checkout
- **THEN** the page header and the browser tab both show "Checkout"

#### Scenario: A sheet does not change the title
- **WHEN** a fan opens `/timetable?concert=<id>`
- **THEN** the browser tab shows "Timetable"
