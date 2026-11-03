## Context

See proposal.md for why. Where the logo lives today:

```
fanart.tv --> ResolveImages --> Fanart{thumb, background, hdlogo, logo, banner}
                                   |
                   best logo --> FetchImage --> AnalyzeLogo --> LogoColorProfile
                                   |
                     artists.fanart (JSONB, the Fanart struct marshalled)
                                   |
             adapter/pb fanartToProto --> entity.v1.Fanart (fields 1-6)
                                   |
         frontend artist-mapper --> ArtistFanart --> bestLogoUrl / artistHueFromColorProfile
                                                     (no template or caller reads either)
```

The backend reads `artists.fanart` by unmarshalling the JSONB into the `entity.Fanart` struct (`artist_repo.go`), and the image sync writes it back by marshalling the same struct. No query reads a JSON path inside the column.

## Goals / Non-Goals

**Goals:** remove the logo kinds, the color profile, the logo download and the color analysis from every repository, with no behavior change on any screen.

**Non-Goals:** `artist_thumb` and `music_banner` stay although no screen shows them today; removing them is a separate decision. The fanart.tv host stays in the app's image Content Security Policy, which the background image needs.

## Decisions

### Reserve the removed proto fields

`Fanart` drops `hd_music_logo = 3`, `music_logo = 4` and `logo_color_profile = 6`, and declares `reserved 3, 4, 6;` and `reserved "hd_music_logo", "music_logo", "logo_color_profile";`. `LogoColorProfile` is deleted. Reserving keeps a future field from reusing the numbers, which an app cached before the change would still decode as the old fields. The plan PR does not touch proto; a separate proto PR carries it with the `buf skip breaking` label (README step 3).

Alternative: mark the fields `deprecated` and keep them. Rejected: nothing reads them, and a deprecated field keeps the generated types and their mapping code alive.

### Release order

The proto release comes first, because backend and frontend only compile without the fields after upgrading to it. Backend and frontend then ship in either order:

- An app built before the change, talking to the new backend, reads the three fields as absent. It already handles that for every artist without a logo, and no screen read them.
- The new app, talking to the old backend, ignores the fields it no longer knows.

### No migration for the stored logo keys

After the change, `entity.Fanart` has no `hdmusiclogo`, `musiclogo` or `logoColorProfile` field. `encoding/json` ignores unknown keys when unmarshalling, so stored keys are never read, and the next `UpdateFanart` of the artist writes the struct without them. Followed artists are synced again within 7 days (`ListStaleOrMissingFanart`). Artists nobody follows keep the keys unread.

Alternative: a migration running `UPDATE artists SET fanart = fanart - 'hdmusiclogo' - 'musiclogo' - 'logoColorProfile'`. Rejected: the keys are invisible and take a few hundred bytes per row, and a migration adds a file, a hash, a test database run and a production check for no observable effect.

### Backend removal

- `entity.Fanart` loses `HDMusicLogo`, `MusicLogo` and `LogoColorProfile`; `entity.LogoColorProfile`, the `LogoImageFetcher` interface (the `Artist.FetchImage` operation) and `AnalyzeLogo` with its color-space helpers go.
- `fanarttv` stops decoding the logo kinds and drops `LogoFetcher`.
- `ArtistImageSyncUseCase` takes the image resolver and the repository only; the event consumer and the daily image sync job stop building the logo fetcher.
- `adapter/pb` stops mapping the logo and the profile.
- The `hd_music_logo`/`music_logo` test data in repository and story tests switch to `artist_background` or `artist_thumb`, keeping what each test checks.

### Frontend removal

- `ArtistFanart` loses `hdMusicLogo`, `musicLogo` and `logoColorProfile`; `LogoColorProfile`, `bestLogoUrl` and `artistHueFromColorProfile` go, with their exports and the mapper's `logoColorProfileFrom`.
- `EventCard` loses `logoUrl`, `logoError`, `onLogoError` and the `eventChanged` reset that only served them; `event-card.css` loses the `.artist-logo` rules. The card's color keeps coming from `artistHue(name)`.
- The unit tests (artist mapper, artist model, guest storage, concert store) and the E2E `artist-image-ui` fixtures that carry logo URLs drop them.

## Risks / Trade-offs

- [A test still asserts a logo field and fails after the upgrade] → the upgrade fails to compile on every remaining reference, so `make check` finds them before the PR.
- [The archive gate needs an `@spec` test for every added or modified scenario, and today none of the image sync, ResolveImages or discover-artists scenarios carries one] → the backend tasks annotate the existing tests that verify them, adding a test where none does.

## Migration Plan

1. Proto PR with `buf skip breaking`, merge, GitHub Release, BSR generation.
2. Backend and frontend PRs, each upgrading to the release, in either order; release each.
3. Read-only in prod after the backend release: the next daily image sync completes, and the image sync consumer logs no error.

Rollback: revert the backend or frontend release; the proto removal stays, and an older backend built before it still compiles against its own pinned version.
