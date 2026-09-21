# Notification

## Purpose

Defines the Notification entity, its payload for a concert-related alert, and its persistence as a uniquely identified record.

## Requirements

### Requirement: Concert notification payload construction

The entity package SHALL provide `NewConcertNotificationPayload(artist *Artist, concertCount int) *NotificationPayload` that constructs a push notification payload for new concert alerts.

The method SHALL:
1. Set the notification title using the artist's name.
2. Set the notification body including the concert count.
3. Include the artist ID in the payload data for deep linking.

#### Scenario: Single concert

- **WHEN** NewConcertNotificationPayload is called with an artist named "YOASOBI" and concertCount=1
- **THEN** the returned payload contains the artist name in the title, mentions 1 concert in the body, and includes the artist ID in data

#### Scenario: Multiple concerts

- **WHEN** NewConcertNotificationPayload is called with concertCount=3
- **THEN** the returned payload body mentions 3 concerts

#### Scenario: Payload data contains artist ID

- **WHEN** NewConcertNotificationPayload is called with artist.ID="artist-abc"
- **THEN** the returned payload data map contains a key mapping to "artist-abc"

---

### Requirement: Notification is persisted as an identified record
Every user-facing notification SHALL be persisted as a durable record with a stable identifier (`notification_id`), the recipient `user_id`, a `type`, the rendered `payload`, and a `created_at` timestamp, before or at the moment it is dispatched. The record is the source of truth; a dispatch failure SHALL NOT cause the notification to be lost.

#### Scenario: A notification is recorded when produced
- **WHEN** a producer asks the notification service to notify a user (e.g. new concerts, a sales reminder)
- **THEN** a notification record SHALL be created with a unique `notification_id`, the `user_id`, the `type`, the `payload`, and `created_at`
- **AND** the record SHALL exist regardless of whether the channel send subsequently succeeds or fails
