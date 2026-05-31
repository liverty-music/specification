## ADDED Requirements

### Requirement: Guest Language as Observable Store State

The guest (anonymous-period) language preference SHALL be owned by `UserStore`
as observable state, unified with the authenticated `User.preferredLanguage`
source. The frontend SHALL NOT read the active guest language through an
unobservable `I18N.getLocale()` call at render time for the purpose of driving
UI state; bindings that depend on the current language SHALL depend on the
store's observable value.

#### Scenario: Guest language exposed as observable
- **WHEN** a guest's preferred language is read for display or selection state
- **THEN** it SHALL be sourced from `UserStore`'s observable current-language
  value (backed by the anonymous-period `language` localStorage key)
- **AND** a change to the guest language SHALL notify dependent bindings so they
  re-evaluate without a manual mirror or a render-time `I18N.getLocale()` read

#### Scenario: Unified resolution across auth states
- **WHEN** the current preferred language is read
- **THEN** `UserStore` SHALL surface `User.preferredLanguage` for an
  authenticated user and the anonymous-period language for a guest
- **AND** callers SHALL NOT branch on `auth.isAuthenticated` to choose the source
