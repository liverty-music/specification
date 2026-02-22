# Proposal: Bottom Navigation Shell

## Problem

The Liverty Music PWA currently uses a top navigation bar with conditional display logic (hidden during onboarding, shown on dashboard). As the app grows beyond the single-page dashboard into multiple primary screens (Discover, My Artists, Settings), the top navigation pattern does not scale. Mobile UX best practices dictate that primary navigation should use a bottom tab bar for thumb-reachable, always-visible access.

## Solution

Replace the current top navigation approach with a **Bottom Navigation Bar (Tab Bar)** as the primary navigation structure. This change creates the shell infrastructure—the tab bar component, routing integration, and placeholder content for each tab—without implementing the full content of each tab.

### Tabs

1. **Home** — Routes to the existing Live Highway Dashboard
2. **Discover** — Placeholder (implemented in a separate change)
3. **My Artists** — Placeholder (implemented in a separate change)
4. **Settings** — Placeholder (implemented in a separate change)

## Scope

### In Scope

- Bottom Navigation Bar component with 4 tabs
- Route configuration for each tab
- Active tab state indication
- Tab bar hidden during onboarding routes (Landing, Artist Discovery, Loading Sequence)
- Tab bar visible on all post-onboarding routes
- Mobile-first responsive design

### Out of Scope

- Full content for Discover, My Artists, Settings tabs (separate changes)
- Mutation UI on Dashboard (separate change: passion-level)
- Any backend changes

## Impact

- Modifies: `app-shell-layout` spec (navigation changes from top bar to bottom tab bar)
- New routes: `/discover`, `/my-artists`, `/settings`
- Existing Dashboard route remains at `/dashboard`

## Dependencies

- None (this is the foundation change)

## Blocked By

- Nothing
