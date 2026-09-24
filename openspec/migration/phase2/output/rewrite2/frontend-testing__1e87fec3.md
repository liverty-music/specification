<!-- spec: frontend-testing | target: components/infrastructure/fan/web/global/auth-status | flags: CLASSNAME | new_name: Auth status delegates to auth service -->

### Requirement: Auth status delegates to auth service
The auth status surface SHALL delegate sign-in, sign-up, and sign-out actions to the auth service.

#### Scenario: Sign in
- **WHEN** `signIn` is called
- **THEN** it SHALL call `auth.signIn()`

#### Scenario: Sign up
- **WHEN** `signUp` is called
- **THEN** it SHALL call `auth.signUp()`

#### Scenario: Sign out
- **WHEN** `signOut` is called
- **THEN** it SHALL call `auth.signOut()`
