# Spec Delta

## Purpose

The reception service boundary called by a reception device: the caller is identified by a ReceptionLink token and a signature made with the private key of the device the link is bound to, not by a sign-in, so venue staff need no account.

## ADDED Requirements

### Requirement: The link and the device's signature are the caller

Open and Admit SHALL accept a call that carries no sign-in. Every call SHALL carry a link token, a signed time and a signature over the token, the call's content and the signed time; Open SHALL also carry the device's public key. A call missing any of them SHALL fail with InvalidArgument before any usecase runs, as SHALL an Admit call without scanned text. The boundary SHALL pass them, with the current time, to ReceptionLinkUseCase.Open or TicketUseCase.Admit, which decide whether the link and the device are allowed.

#### Scenario: Staff device without an account

- **WHEN** a device with no sign-in calls Open with a valid link token, its public key and a signature
- **THEN** the call reaches ReceptionLinkUseCase.Open

#### Scenario: Missing signature

- **WHEN** Admit is called without a signature
- **THEN** it fails with InvalidArgument and nothing is admitted

### Requirement: Guessing links is throttled

Once a client has made 10 calls with unknown link tokens within 10 minutes, the boundary SHALL refuse every further call from that client with ResourceExhausted until 10 minutes have passed since the first of those calls.

#### Scenario: Token guessing

- **WHEN** a client calls Open with 11 different unknown link tokens within 10 minutes
- **THEN** the 11th call fails with ResourceExhausted
