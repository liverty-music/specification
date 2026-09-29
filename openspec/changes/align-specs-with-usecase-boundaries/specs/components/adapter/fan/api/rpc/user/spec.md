# Spec Delta

## MODIFIED Requirements

### Requirement: Per-user calls act only on the caller's own account

Get, UpdatePreferredLanguage, UpdateHome and ResendEmailVerification SHALL each name the target User by id. The boundary SHALL fail with InvalidArgument when the id is missing or is not a well-formed id. Get, UpdatePreferredLanguage and UpdateHome SHALL then resolve the caller through UserUseCase.ResolveCaller with the caller's identity and the named id, and return its failure unchanged: NotFound when the caller has no User, and PermissionDenied when the named id is not the caller's, before any other read or any change. ResendEmailVerification leaves the same check to UserUseCase.ResendEmailVerification.

#### Scenario: Own account

- **WHEN** a signed-in caller names their own User id
- **THEN** the call proceeds for the caller's User

#### Scenario: Another user's account

- **WHEN** a signed-in caller names a different User's id
- **THEN** the call fails with PermissionDenied and nothing is returned or changed

#### Scenario: Missing user id

- **WHEN** a signed-in caller names no User id
- **THEN** the call fails with InvalidArgument

#### Scenario: Caller has no account

- **WHEN** the signed-in caller's identity has no User
- **THEN** the call fails with NotFound

## ADDED Requirements

### Requirement: ResendEmailVerification is decided by the usecase

ResendEmailVerification SHALL call UserUseCase.ResendEmailVerification with the caller's sign-in identity and the named User id, and return its failure unchanged. Whether verification is available, the caller check, and the limit of 3 resends per 10 minutes per User are that usecase's rules.

#### Scenario: Caller resends their own email

- **WHEN** a signed-in caller requests a resend for their own unverified account
- **THEN** a fresh verification email is sent

#### Scenario: Usecase failure returned unchanged

- **WHEN** UserUseCase.ResendEmailVerification fails with ResourceExhausted
- **THEN** ResendEmailVerification fails with ResourceExhausted

## REMOVED Requirements

### Requirement: Resending the caller's verification email

**Reason**: The availability check, the caller check and the limit of 3 resends per 10 minutes per User moved from the boundary into UserUseCase.ResendEmailVerification; the boundary only passes the caller's identity and the named User id and returns the usecase's result.

**Migration**: Replaced by "ResendEmailVerification is decided by the usecase"; the rules and their scenarios are in components/usecase/user/resend-email-verification.
