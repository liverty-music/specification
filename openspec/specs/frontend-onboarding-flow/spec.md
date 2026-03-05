## MODIFIED Requirements

### Requirement: Landing Page with Authentication

The system SHALL provide a landing page that communicates the service value proposition and provides entry points for both new users (tutorial) and returning users (direct login). Authentication is no longer required at the landing page; new users enter a guest tutorial flow.

#### Scenario: First-time user visits landing page

- **WHEN** a user accesses the application for the first time
- **THEN** the system SHALL display a hero message communicating the core value ("大好きなあのバンドのライブ、もう二度と見逃さない。")
- **AND** the system SHALL display a sub-message ("あなたの推しアーティストを登録するだけで、全国のライブ日程を自動収集。")
- **AND** the system SHALL provide a primary [Get Started] CTA button that enters the tutorial flow without authentication
- **AND** the system SHALL provide a secondary [Login] text link for returning users
- **AND** the system SHALL NOT provide "Sign Up" or "Sign In" buttons that trigger immediate authentication

#### Scenario: User taps Get Started

- **WHEN** a user taps the [Get Started] button
- **THEN** the system SHALL set `onboardingStep` to 1 in LocalStorage
- **AND** the system SHALL navigate to the Artist Discovery page (`/onboarding/discover`)
- **AND** the system SHALL NOT require authentication

#### Scenario: User taps Login

- **WHEN** a user taps the [Login] link
- **THEN** the system SHALL initiate the Zitadel OIDC flow for Passkey authentication
- **AND** upon successful authentication, the system SHALL redirect to the Dashboard with full unrestricted access

#### Scenario: User provisioning fails during login callback

- **WHEN** the OIDC callback processing fails
- **THEN** the system SHALL display an error message on the callback page
- **AND** the system SHALL provide a "Return to Home" link

### Requirement: Just-in-Time Region Configuration

The system SHALL collect the user's home area during the Dashboard reveal step of the tutorial (Step 3), presenting the home area selector as a BottomSheet overlay before displaying personalized content. The selector SHALL use the same 2-step region-to-prefecture flow used throughout the application.

#### Scenario: Home area setup overlay on Dashboard reveal (Step 3)

- **WHEN** the user arrives at the Dashboard during the tutorial (Step 3)
- **AND** the user has not yet configured their home area
- **THEN** the system SHALL display the Dashboard with a blurred background
- **AND** the system SHALL present the `user-home-selector` BottomSheet overlay as a native `<dialog>` element via `showModal()`, promoted to the browser's Top Layer (no z-index stacking)
- **AND** the selector SHALL display Step 1 with quick-select major city buttons (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai) and region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** the BottomSheet SHALL use the design system's dark surface palette and sheet radius token

#### Scenario: Quick-select city in onboarding

- **WHEN** the user taps a quick-select city button in Step 1
- **THEN** the system SHALL immediately confirm the selection with the city's prefecture code (e.g., Tokyo -> JP-13)
- **AND** the system SHALL NOT display Step 2

#### Scenario: Region-to-prefecture selection in onboarding

- **WHEN** the user taps a region button in Step 1
- **THEN** the system SHALL transition to Step 2 showing prefectures within the selected region
- **AND** Step 2 SHALL include a back button to return to Step 1
- **WHEN** the user taps a prefecture in Step 2
- **THEN** the system SHALL confirm the selection with the prefecture's ISO 3166-2 code

#### Scenario: Magic moment after home area selection

- **WHEN** the user selects their home area (via quick-select or region-to-prefecture)
- **THEN** the system SHALL store the selected code in localStorage under `guest.home`
- **AND** the system SHALL immediately close the BottomSheet
- **AND** the system SHALL unblur the Dashboard background with a smooth transition animation
- **AND** the system SHALL dynamically populate the Live Highway UI with home-area-relevant events

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During the tutorial, followed artists are stored locally (not via backend RPC). Additionally, the system SHALL trigger a background concert search for each followed artist to pre-populate concert data for the Dashboard.

#### Scenario: Initial artist bubble display

- **WHEN** a user reaches the Artist Discovery step (Step 1)
- **THEN** the system SHALL call Last.fm's `geo.getTopArtists` API with `country=japan`
- **AND** the system SHALL display approximately 30 top artists as floating circular bubbles with physics-based animation

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in tutorial) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in `liverty:guest:followedArtists` in LocalStorage
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself
- **AND** the system SHALL call `ConcertService/SearchNewConcerts` fire-and-forget in the background
- **AND** errors from `SearchNewConcerts` SHALL be logged to console and NOT affect the follow operation or UI

#### Scenario: Progress bar reaches target

- **WHEN** the user has followed 3 or more artists
- **THEN** the system SHALL display the progress bar at 100%
- **AND** the system SHALL activate and highlight the [Generate Dashboard] CTA button

#### Scenario: Discover to Dashboard transition

- **WHEN** a user is at Step 1 (Artist Discovery)
- **AND** the user has followed >= 3 artists
- **AND** the user taps the [Generate Dashboard] CTA
- **THEN** the system SHALL set `onboardingStep` to 3 (DASHBOARD)
- **AND** the system SHALL navigate to `/dashboard`
- **AND** the system SHALL NOT navigate to `/onboarding/loading`

#### Scenario: Concert data availability at Dashboard

- **WHEN** the user arrives at the Dashboard after completing Artist Discovery
- **THEN** concert data MAY already be available from the fire-and-forget `SearchNewConcerts` calls triggered during artist follows in Discovery
- **AND** the Dashboard SHALL display its own loading skeleton / promise states for any data still pending
- **AND** the system SHALL NOT rely on a loading screen to mask data fetching
