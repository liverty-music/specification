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

The system SHALL collect the user's primary residential area during the Dashboard reveal step of the tutorial (Step 3), presenting the region selector as a BottomSheet overlay before displaying personalized content.

#### Scenario: Region setup overlay on Dashboard reveal (Step 3)

- **WHEN** the user arrives at the Dashboard during the tutorial (Step 3)
- **AND** the user has not yet configured their region
- **THEN** the system SHALL display the Dashboard with a blurred background
- **AND** the system SHALL present a BottomSheet overlay with the message "To find live events near you, tell us your main area"
- **AND** the system SHALL provide a prefecture dropdown selector or quick-select buttons for major cities
- **AND** the BottomSheet SHALL use the design system's dark surface palette and sheet radius token

#### Scenario: Magic moment after region selection

- **WHEN** the user selects their region in the BottomSheet
- **THEN** the system SHALL store the selected region in `liverty:guest:region` in LocalStorage
- **AND** the system SHALL immediately close the BottomSheet
- **AND** the system SHALL unblur the Dashboard background with a smooth transition animation
- **AND** the system SHALL dynamically populate the Live Highway UI with region-relevant events

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During the tutorial, followed artists are stored locally (not via backend RPC).

#### Scenario: Initial artist bubble display

- **WHEN** a user reaches the Artist Discovery step (Step 1)
- **THEN** the system SHALL call Last.fm's `geo.getTopArtists` API with `country=japan`
- **AND** the system SHALL display approximately 30 top artists as floating circular bubbles with physics-based animation

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in tutorial) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist in `liverty:guest:followedArtists` in LocalStorage
- **AND** the system SHALL NOT call any backend RPC

#### Scenario: Progress bar reaches target

- **WHEN** the user has followed 3 or more artists
- **THEN** the system SHALL display the progress bar at 100%
- **AND** the system SHALL activate and highlight the [Generate Dashboard] CTA button
