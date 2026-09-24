# LotteryUseCase.DrawDuePhases

## Purpose

LotteryUseCase.DrawDuePhases draws every LotterySalesPhase whose window has closed and which has not been drawn yet.

## Requirements

### Requirement: Draw within one minute after the window closes

DrawDuePhases SHALL run every 1 minute. It SHALL list the phases due at the current time with LotterySalesPhase.ListPhasesDueForDraw and run LotteryUseCase.RunDraw for each. A phase whose draw fails SHALL NOT stop the others and stays due, so it is tried again on the next run. When the listing fails, DrawDuePhases SHALL fail with that error and draw nothing.

#### Scenario: Window closes

- **WHEN** a phase's close time passes
- **THEN** the phase is drawn within 1 minute

#### Scenario: Window still open

- **WHEN** a phase's close time has not passed
- **THEN** it is not drawn

#### Scenario: Drawn once

- **WHEN** a phase has been drawn
- **THEN** later runs do not draw it again

#### Scenario: One phase fails

- **WHEN** the draw of one due phase fails
- **THEN** the other due phases are still drawn and the failed phase is tried again 1 minute later
