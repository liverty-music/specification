# LotteryUseCase.RunDraw

## Purpose

LotteryUseCase.RunDraw draws one closed LotterySalesPhase: it orders the Applied applications at random, admits whole applications that fit the capacity, captures each winner's hold, releases every other hold, and records the outcome with the losers' draw order.

## Requirements

### Requirement: Draw a phase

RunDraw SHALL read the phase with LotterySalesPhase.Get, failing with NotFound when it does not exist, take the phase's Applied applications from TicketApplication.ListAppliedForPhase, and compute the outcome with TicketApplication.RunLotteryDraw against the phase's ticket capacity, using an unpredictable random order. It SHALL capture each winner's hold with TicketApplication.CaptureAuthorization, release each waitlisted application's hold with TicketApplication.CancelAuthorization, and record the outcome with TicketApplication.PersistDrawOutcome: captured winners Won, every other application Lost, each with its draw position. When the phase has no Applied application, it SHALL only mark the phase drawn.

#### Scenario: Winners charged, losers released

- **WHEN** a closed phase with capacity 4 has applications for 2, 2 and 3 tickets and the random order admits the two 2-ticket applications
- **THEN** their holds are captured and they are Won, the 3-ticket application's hold is released and it is Lost, and the phase is drawn

#### Scenario: Losers ordered for the waitlist

- **WHEN** the draw completes with Lost applications
- **THEN** each Lost application carries its draw position, so the waitlist can be read in draw order

#### Scenario: No applications

- **WHEN** the phase has no Applied application
- **THEN** the phase is marked drawn and nothing is captured or released

### Requirement: Capture failure

When a winner's capture fails, RunDraw SHALL release that application's hold, record it Lost with its draw position so it joins the waitlist, and leave its tickets unallocated; no waitlisted application is promoted (no 繰上げ, promotion from the waitlist).

#### Scenario: Winner's card was closed

- **WHEN** TicketApplication.CaptureAuthorization fails for a winner
- **THEN** its hold is released, it is Lost with its draw position, and its tickets stay unallocated

### Requirement: Release failure does not stop the draw

When releasing a loser's hold fails, RunDraw SHALL still record the application Lost and continue.

#### Scenario: Release fails for one loser

- **WHEN** TicketApplication.CancelAuthorization fails for a waitlisted application
- **THEN** the application is still recorded Lost and the rest of the draw completes

### Requirement: The draw issues nothing

RunDraw SHALL NOT create an Order or a Ticket; a Won application is the only input to IssuanceUseCase.IssueFromCapturedWin.

#### Scenario: After the draw

- **WHEN** RunDraw records an application Won
- **THEN** no Order or Ticket exists for it yet
