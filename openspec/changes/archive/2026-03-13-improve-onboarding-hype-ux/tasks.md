## 1. Backend: Default Hype Change

- [x] 1.1 Change default hype from HOME to WATCH in FollowArtist handler
- [x] 1.2 Update unit tests for FollowArtist to assert WATCH default

## 2. Frontend: Hype Inline Slider Component

- [x] 2.1 Create `hype-inline-slider` component with 4-stop dot slider (track, dots, active dot with artist-color glow)
- [x] 2.2 Implement hype-tier CSS effects on active dot (WATCH/HOME/NEARBY/AWAY glow matching passion-level card styles)
- [x] 2.3 Add 44×44px tap target areas and 200ms slide transition animation
- [x] 2.4 Add `prefers-reduced-motion` support (disable pulse/gradient animations)
- [x] 2.5 Wire authenticated tap handler: optimistic update + SetHype RPC + rollback on failure
- [x] 2.6 Wire unauthenticated tap handler: dispatch `hype-signup-prompt` event, block slider movement

## 3. Frontend: My Artists Page Redesign

- [x] 3.1 Add sticky header with hype legend (👀🔥🔥🔥🔥🔥🔥🔥 + emotion labels), `position: sticky`, `backdrop-filter: blur`, `[data-hype-header]` attribute
- [x] 3.2 Refactor artist list row: single-line layout with name (flex-shrink, ellipsis) + inline slider (flex-grow)
- [x] 3.3 Align slider dot positions with header legend columns via shared CSS Grid template
- [x] 3.4 Remove bottom sheet passion level selector from list view
- [x] 3.5 Update emotion-based tier labels in HYPE_META (チェック/地元/近くも/どこでも！)

## 4. Frontend: Notification Dialog

- [x] 4.1 Create notification dialog component (single-page: hype tier → notification scope mapping + signup CTA + "あとで" button)
- [x] 4.2 Handle `hype-signup-prompt` event on My Artists page to show notification dialog
- [x] 4.3 Implement "アカウント作成" button: initiate Zitadel OIDC Passkey flow, trigger guest data merge on success
- [x] 4.4 Implement "あとで" button: close dialog, show inline signup banner
- [x] 4.5 Add once-per-session guard (dialog not shown again after "あとで" dismissal)

## 5. Frontend: Signup Prompt Banner

- [x] 5.1 Create shared `signup-prompt-banner` component with configurable message and signup CTA
- [x] 5.2 Add banner to My Artists page (after last artist row, within scroll content)
- [x] 5.3 Add banner to Dashboard page (after lane grid, within scroll content)
- [x] 5.4 Add conditional rendering: show only when unauthenticated and onboarding completed or dialog dismissed
- [x] 5.5 Auto-remove banner when isAuthenticated becomes true

## 6. Frontend: Onboarding Flow Updates

- [x] 6.1 Update Step 5 coachmark: target `[data-hype-header]`, message "絶対に見逃したくないアーティストの熱量を上げておこう"
- [x] 6.2 Change Step 5 coachmark dismissal to advance directly to Step 7 (COMPLETED)
- [x] 6.3 Remove Step 6 signup modal component and its entrance animation CSS
- [x] 6.4 Remove passion explanation dialog and 800ms delay timer
- [x] 6.5 Add backward compatibility: if onboardingStep=6 found in localStorage, advance to 7
- [x] 6.6 Remove Step 5 → Step 6 transition logic from OnboardingService

## 7. Testing

- [x] 7.1 Unit test: hype-inline-slider authenticated tap (optimistic update + RPC)
- [x] 7.2 Unit test: hype-inline-slider unauthenticated tap (event dispatch, no slider movement)
- [x] 7.3 Unit test: notification dialog once-per-session guard
- [x] 7.4 Unit test: signup-prompt-banner conditional rendering
- [x] 7.5 Unit test: onboarding Step 5 → Step 7 progression (skip Step 6)
- [x] 7.6 Unit test: backward compat for onboardingStep=6 in localStorage
