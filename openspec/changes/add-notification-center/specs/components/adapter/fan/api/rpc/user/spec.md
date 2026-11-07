## MODIFIED Requirements

### Requirement: Create registers the signed-in identity

Create SHALL name no User id. It SHALL take the provider user ID, email and name from the caller's sign-in identity and never from the request; the request SHALL still carry a well-formed email, which is ignored. It SHALL take the preferred language and the optional Home from the request, fail with InvalidArgument when the preferred language is missing or not exactly two lowercase letters or a Home in the request is malformed, and otherwise call UserUseCase.Create and return the User it returns.

#### Scenario: First sign-in

- **WHEN** a signed-in caller whose identity has no User calls Create with preferred language `ja`
- **THEN** a User is registered with the email and name of the sign-in identity and preferred language `ja`, and returned

#### Scenario: Request email differs from the identity

- **WHEN** the request carries an email different from the sign-in identity's email
- **THEN** the User is registered with the sign-in identity's email

#### Scenario: Returning identity

- **WHEN** a signed-in caller whose identity already has a User calls Create
- **THEN** that existing User is returned

#### Scenario: Missing email in the request

- **WHEN** the request carries no email
- **THEN** Create fails with InvalidArgument

#### Scenario: Missing preferred language

- **WHEN** the request carries no preferred language
- **THEN** Create fails with InvalidArgument
