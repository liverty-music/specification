## Architecture

All changes are in the backend repository. Follows the existing EDA patterns established in `introduce-eda`.

## Event Flow

```
  Search / ListSimilar / ListTop
           │
           ▼
  persistArtists(ctx, artists)
           │
    ┌──────┴──────┐
    │ ListByMBIDs │ → existing (skip)
    └──────┬──────┘
           │
    ┌──────┴──────┐
    │   Create    │ → newly inserted
    └──────┬──────┘
           │
           ▼
  for each new artist:
    publish ARTIST.created  ← NEW
           │
           ▼
  merge existing + created → return

  ════════════════════════════════════
  Consumer Process (async)
  ════════════════════════════════════

  ARTIST.created event
         │
         ▼
  ArtistNameConsumer.Handle()
         │
         ▼
  MusicBrainz GetArtist(mbid)     ← 1 req/sec (natural throttle)
         │
         ▼
  if canonical name != current name:
      artistRepo.UpdateName(id, canonicalName)
  else:
      no-op (ack message)
```

## ARTIST Stream Configuration

```go
// streams.go
{
    Name:       "ARTIST",
    Subjects:   []string{"ARTIST.*"},
    Retention:  nats.LimitsPolicy,
    MaxAge:     7 * 24 * time.Hour,
    Storage:    nats.FileStorage,
    Discard:    nats.DiscardOld,
    Replicas:   1,
    Duplicates: 2 * time.Minute,
}
```

Follows the same configuration pattern as `CONCERT` and `VENUE` streams.

## Event Payload

```go
// events.go
type ArtistCreatedData struct {
    ArtistID   string `json:"artist_id"`
    ArtistName string `json:"artist_name"`
    MBID       string `json:"mbid"`
}
```

Subject constant: `SubjectArtistCreated = "ARTIST.created"`

## Publisher Integration in UseCase

The `artistUseCase` gains a `message.Publisher` dependency. The `persistArtists` helper publishes after step 4 (Create missing):

```go
for _, a := range created {
    msg, err := messaging.NewEvent(messaging.ArtistCreatedData{
        ArtistID:   a.ID,
        ArtistName: a.Name,
        MBID:       a.MBID,
    })
    if err != nil {
        uc.logger.Warn(ctx, "failed to create artist.created event", ...)
        continue
    }
    if err := uc.publisher.Publish(messaging.SubjectArtistCreated, msg); err != nil {
        uc.logger.Warn(ctx, "failed to publish artist.created event", ...)
    }
}
```

Event publish failures are logged and swallowed — they must not block the search response. The artist is already persisted; name resolution is best-effort enrichment.

## ArtistNameConsumer

```go
// adapter/event/artist_consumer.go
type ArtistNameConsumer struct {
    artistRepo entity.ArtistRepository
    idManager  entity.ArtistIdentityManager
    logger     *logging.Logger
}

func (h *ArtistNameConsumer) Handle(msg *message.Message) error {
    ctx := context.Background()

    var data messaging.ArtistCreatedData
    if err := messaging.ParseCloudEventData(msg, &data); err != nil {
        return fmt.Errorf("parse artist.created event: %w", err)
    }

    canonical, err := h.idManager.GetArtist(ctx, data.MBID)
    if err != nil {
        return fmt.Errorf("resolve canonical name: %w", err)
    }

    if canonical.Name == data.ArtistName {
        return nil // name already correct
    }

    if err := h.artistRepo.UpdateName(ctx, data.ArtistID, canonical.Name); err != nil {
        return fmt.Errorf("update artist name: %w", err)
    }

    return nil
}
```

Watermill retry middleware (3 retries, exponential backoff) handles MusicBrainz rate limit errors naturally. Failed messages go to the poison queue after max retries.

## New Repository Method: `UpdateName`

### Interface Addition

```go
// entity/artist.go — added to ArtistRepository interface

// UpdateName updates the display name of an artist identified by ID.
UpdateName(ctx context.Context, id string, name string) error
```

### SQL

```sql
UPDATE artists SET name = $2 WHERE id = $1
```

## DI Wiring

### provider.go (server process)

Pass `publisher` to `NewArtistUseCase` so `persistArtists` can publish events.

### consumer.go (consumer process)

```go
artistNameConsumer := event.NewArtistNameConsumer(artistRepo, musicbrainzClient, logger)

router.AddConsumerHandler(
    "resolve-artist-name",
    messaging.SubjectArtistCreated,
    subscriber,
    artistNameConsumer.Handle,
)
```

The MusicBrainz client is already instantiated in `consumer.go` for venue enrichment. Reuse the same instance.

## Decisions

- **Fire-and-forget publishing**: Event publish errors are logged but do not fail the search. Artist data is already in the DB; name resolution is eventual enrichment.
- **MusicBrainz rate limit**: The consumer processes one message at a time per consumer instance. At 1 req/sec MusicBrainz limit, this is naturally compliant. KEDA scaling should cap consumer replicas to avoid exceeding the rate limit.
- **Idempotency**: Re-processing `ARTIST.created` is safe — `UpdateName` is a simple SET that converges to the correct state regardless of how many times it runs.
