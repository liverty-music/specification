## Context

The current frontend (`welcome-page`) is a placeholder with no product messaging or auth integration. The `auth-service` and `auth-callback` route already exist and handle the Zitadel OIDC flow with Passkey authentication (Passkeys-only policy configured in Zitadel), but there is no dedicated landing page that funnels first-time users into sign-up.

The Artist Discovery step (`frontend-artist-discovery-ui`) is being implemented in a separate worktree and is near completion. The landing page is the immediate predecessor in the onboarding flow.

## Goals / Non-Goals

**Goals:**
- Create a visually compelling, mobile-first landing page with hero copy and Sign Up / Sign In CTA (Passkey auth via Zitadel).
- Route authenticated users to the correct next step (Artist Discovery for new users, Dashboard for returning users).
- Maintain sub-second load time for the landing page (no heavy assets).

**Non-Goals:**
- Multi-provider OAuth (Google, Spotify, Apple Music, YouTube) — out of MVP scope; Passkey-only.
- Email/password sign-up — Passkey-only via Zitadel.
- A/B testing of hero copy — future concern.
- SEO optimization beyond basic meta tags — PWA focus.

## Decisions

### 1. Replace WelcomePage In-Place
**Decision**: Replace the existing `WelcomePage` component content rather than creating a new route.
**Rationale**: The root route (`/`) should serve as the landing page. No need for an additional route. The existing routing structure already handles `/` → `WelcomePage`.

### 2. Auth State-Based Routing
**Decision**: Use the existing `auth-service` to check authentication status on the landing page. If already authenticated, redirect immediately.
**Rationale**: Prevents authenticated users from seeing the sign-up page. The `auth-service` already provides `isAuthenticated` state.

**Post-auth redirect flow:**
```
Landing Page (/)
  → [Click "Sign Up" / "Sign In"]
  → Zitadel OIDC flow (Passkey authentication)
  → /auth/callback
  → Check onboarding status
  → /onboarding/discover (new user)
  → /dashboard (returning user)
```

### 3. Onboarding Completion Check
**Decision**: Use the `ListFollowedArtists` RPC to determine onboarding completion. If the user has ≥1 followed artist, they are considered onboarded and routed to the Dashboard.
**Rationale**: Simple heuristic that avoids adding a separate "onboarding_completed" flag. A user who has followed at least one artist has completed the discovery step.

### 4. Styling Approach
**Decision**: Use Tailwind CSS utility classes, consistent with the existing frontend setup.
**Rationale**: The project already uses Tailwind. The landing page is primarily typography and a button — no complex component library needed.

## Risks / Trade-offs

- **[Risk] Auth redirect loop** → If auth state is stale, the user could be redirected back to landing.
  - **Mitigation**: Check token validity on landing page load; clear stale tokens before rendering.
- **[Trade-off] No server-side rendering** → First paint depends on JS bundle load.
  - **Mitigation**: Keep the landing page component minimal (no heavy imports). Consider inlining critical CSS.
- **[Risk] Onboarding heuristic false positive** → A user who unfollowed all artists would be treated as "not onboarded."
  - **Mitigation**: Acceptable for MVP. Can add explicit onboarding status later if needed.
