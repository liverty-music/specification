# Follow.ListFollowers

## Purpose

Lists the fans who follow one artist, with what is needed to decide and word a push to each of them.

## Requirements

### Requirement: ListFollowers returns each follower with hype, home and language

ListFollowers SHALL return one entry per Follow of the artist, carrying the fan's id, the Follow's hype level, the fan's preferred language, and the fan's home: its home area and the home area's centre. A fan without a home SHALL be returned with no home. When nobody follows the artist, ListFollowers SHALL return an empty list, not an error.

Known defect: liverty-music/backend#469

#### Scenario: Follower with a home

- **WHEN** a fan whose home area is JP-13 follows the artist at Nearby
- **THEN** the entry carries hype level Nearby, the home area JP-13 and that area's centre

#### Scenario: Follower without a home

- **WHEN** a fan with no home follows the artist
- **THEN** the entry carries no home

#### Scenario: No followers

- **WHEN** nobody follows the artist
- **THEN** an empty list is returned
