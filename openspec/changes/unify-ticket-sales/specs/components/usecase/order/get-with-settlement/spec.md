# Spec Delta

## Purpose

OrderUseCase.GetWithSettlement reads one Order together with its Settlement, for an admin who supports a fan or reconciles a payout.

## ADDED Requirements

### Requirement: An Order with its Settlement

GetWithSettlement SHALL read the Order with Order.Get, failing with NotFound when it does not exist, then read its Settlement with Settlement.GetByOrderID and return both. When the Order has no Settlement, it SHALL return the Order alone; that is not an error. Other failures SHALL be returned unchanged.

#### Scenario: Order with a held settlement
- **WHEN** an Order's payout is Held
- **THEN** GetWithSettlement returns the Order and its Held Settlement with its splits

#### Scenario: Order with no settlement yet
- **WHEN** the Order has no Settlement
- **THEN** GetWithSettlement returns the Order and no Settlement

#### Scenario: Order not found
- **WHEN** no Order has the id
- **THEN** GetWithSettlement fails with NotFound
