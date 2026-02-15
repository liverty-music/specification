## 1. Landing Page Component

- [ ] 1.1 Replace `WelcomePage` component with `LandingPage` (hero heading, sub-heading, layout structure)
- [ ] 1.2 Add "Sign Up" (calls `auth-service.register()`) and "Sign In" (calls `auth-service.signIn()`) CTA buttons for Passkey authentication
- [ ] 1.3 Implement mobile-first responsive styling (centered hero, full-width CTA, no horizontal scroll)

## 2. Post-Authentication Routing

- [ ] 2.1 Update `auth-callback` route to check onboarding status via `ListFollowedArtists` RPC after token exchange
- [ ] 2.2 Implement conditional redirect: `/onboarding/discover` (no followed artists) vs `/dashboard` (≥1 followed artist)
- [ ] 2.3 Add authenticated-user redirect on landing page (skip landing if already authenticated)

## 3. Route Configuration

- [ ] 3.1 Register `/onboarding/discover` route placeholder for Artist Discovery handoff
- [ ] 3.2 Register `/dashboard` route placeholder for Dashboard handoff
- [ ] 3.3 Update root route `/` to use `LandingPage` component
