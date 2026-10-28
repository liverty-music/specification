## Purpose

A fan who wants to go to a live show soon finds the concerts near their area within a chosen period, including concerts of artists they do not follow yet, and follows an artist from one of those concerts so that its concerts reach their timetable.

```mermaid
usecase-beta
direction LR
actor Fan("fan")
systemBoundary "Liverty Music"
  Goal("Find concerts nearby")
  ConcertUseCaseListByLocation("ConcertUseCase.ListByLocation")
  FollowUseCaseFollow("FollowUseCase.Follow")
end
Fan --> Goal
Goal ..> : include ConcertUseCaseListByLocation
Goal ..> : include FollowUseCaseFollow
```

## ADDED Requirements

### Requirement: The concerts near the fan's area are listed for a period

From Discovery the fan SHALL reach, in one tap on the swap tile, the concerts that ConcertUseCase.ListByLocation returns for the fan's home area (or an area chosen for the visit) and the chosen period: concerts in the area as HOME, concerts in another area within 200 km as NEAR, whether or not the fan follows their artists. Concerts farther away SHALL NOT be listed.

#### Scenario: A weekend near home
- **WHEN** a guest whose home area is Fukuoka opens Discovery, taps the swap tile and picks 今週末
- **THEN** this weekend's concerts in Fukuoka are listed under HOME and those in Kumamoto under NEAR, including artists the guest does not follow
- **AND** a concert in Tokyo the same weekend is not listed

#### Scenario: No home area yet
- **WHEN** a guest without a home area opens the All Nearby view
- **THEN** the guest is asked to choose an area before any concert is listed

### Requirement: Following from a nearby concert adds the artist to the timetable

When a signed-in fan follows the artist of a concert from the All Nearby view, FollowUseCase.Follow SHALL store the follow, and the artist's concerts SHALL appear on the fan's dashboard timetable. A guest who taps the follow action SHALL be offered sign-up instead, and no follow is stored.

#### Scenario: Signed-in fan follows from a nearby concert
- **WHEN** a signed-in fan opens a nearby concert of an artist they do not follow and taps 「このアーティストをフォロー」
- **THEN** the artist appears in My Artists at hype level Nearby and its concerts appear on the dashboard timetable

#### Scenario: Guest taps follow
- **WHEN** a guest taps 「このアーティストをフォロー」 on a nearby concert
- **THEN** the sign-up prompt banner appears and the guest follows no artist
