# Proposal: Settings Page

## Problem

Users currently have limited access to account management and system preferences. Sign-out is embedded in the top navigation bar, and there is no UI for changing the registered area (prefecture) or managing push notification preferences. As the app transitions to a bottom tab bar navigation, a dedicated Settings tab is needed.

## Solution

Implement the **Settings page** (Tab 4) with the following sections:

1. **My Area** — Change registered prefecture using the same 2-tap UI from onboarding (region → prefecture)
2. **Push Notifications** — Global ON/OFF toggle for push notifications
3. **About** — Links to Terms of Service, Privacy Policy, and OSS licenses
4. **Account** — Sign Out button

## Scope

### In Scope

- Settings page UI with grouped list layout
- My Area change via bottom sheet (region → prefecture selector)
- Push notification toggle
- About section with static links
- Sign Out button with existing auth flow integration

### Out of Scope

- Granular notification filtering (e.g., "Must Go only") — part of passion-level change
- Profile editing, linked account management (post-MVP)
- Backend changes for area/notification preferences (frontend-only state for MVP)

## Impact

- New spec: `settings`
- Depends on: `bottom-navigation-shell` (provides the tab and route)

## Dependencies

- `bottom-navigation-shell` (route `/settings` and tab must exist)

## Blocked By

- `bottom-navigation-shell`
