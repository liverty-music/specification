# Spec Delta

## Purpose

Tells whether the cardholder verified an Order's captured payment, through the card issuer's authentication (3D Secure) or a device wallet's: the evidence that the cardholder authorized it.

## ADDED Requirements

### Requirement: Verification of the payment

IsCardholderAuthenticated SHALL return true when the card issuer authenticated the cardholder for the Order's captured payment, or when the payment was made with a device wallet that authenticated the cardholder, and false otherwise, including when the issuer only acknowledged an authentication attempt. It SHALL fail with FailedPrecondition when the Order has no captured payment, with NotFound when no Order has the id, and with Unavailable when the payment provider cannot be reached.

#### Scenario: Authenticated payment
- **WHEN** the fan passed the card issuer's authentication when paying the Order
- **THEN** IsCardholderAuthenticated returns true

#### Scenario: Wallet payment
- **WHEN** the fan paid the Order with a device wallet
- **THEN** IsCardholderAuthenticated returns true

#### Scenario: Attempt only acknowledged
- **WHEN** the card issuer only acknowledged an authentication attempt for the Order's payment
- **THEN** IsCardholderAuthenticated returns false

#### Scenario: No authentication
- **WHEN** the Order's payment was authorized without any authentication
- **THEN** IsCardholderAuthenticated returns false

#### Scenario: Order never paid
- **WHEN** the Order is Pending
- **THEN** IsCardholderAuthenticated fails with FailedPrecondition
