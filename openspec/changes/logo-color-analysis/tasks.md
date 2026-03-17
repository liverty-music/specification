## 0. Specification: Proto Schema

- [x] 0.1 Add `LogoColorProfile` message to `artist.proto` with `dominant_hue` (float), `dominant_lightness` (float), `is_chromatic` (bool)
- [x] 0.2 Add `optional LogoColorProfile logo_color_profile = 6` field to the `Fanart` message
- [x] 0.3 Run `buf lint` and `buf format -w`
- [x] 0.4 Create specification PR (#276), merge, create release → BSR publishes

## 1. Backend: Color Extraction (Entity Layer — Pure Functions)

- [ ] 1.1 Add `LogoColorProfile` struct to `entity/fanart.go` with `DominantHue *float64` (pointer for optional presence), `DominantLightness float64`, `IsChromatic bool` and JSON tags
- [ ] 1.2 Add `LogoColorProfile *LogoColorProfile` field to `Fanart` struct with `json:"logoColorProfile,omitempty"` tag
- [ ] 1.3 Implement `oklch.go` in `entity/` with sRGB→LinearRGB→OKLab→OKLCH conversion (pure math, no external deps)
- [ ] 1.4 Unit test `oklch.go`: pure white → L≈1.0 C≈0.0, pure red → L≈0.63 C>0.2 H≈29°, pure black → L≈0.0 C≈0.0
- [ ] 1.5 Implement `AnalyzeLogo(img image.Image) *LogoColorProfile` in `entity/fanart.go`: pure function, no I/O. Skip transparent pixels, build hue histogram, classify chromatic/achromatic, return profile
- [ ] 1.6 Unit test `AnalyzeLogo` with synthetic `image.NRGBA` images: chromatic image (>30% colored pixels), achromatic light image, achromatic dark image, fully transparent image → nil

## 2. Backend: Sync Pipeline Integration (Usecase Layer — Orchestration)

- [ ] 2.1 Add usecase method that orchestrates logo color profiling: select best logo URL via `BestByLikes` (HDMusicLogo → MusicLogo fallback) — same selection as the proto mapper — then HTTP GET, `image/png` decode, call `AnalyzeLogo`
- [ ] 2.2 Update `SyncArtistImages` (CronJob path) to call the profiling method and set `fanart.LogoColorProfile` before persisting
- [ ] 2.3 Update ARTIST.created consumer to call the profiling method after fetching fanart data
- [ ] 2.4 Handle logo download failures gracefully: log warning, proceed with nil LogoColorProfile (non-fatal)
- [ ] 2.5 Run `make check` in backend

## 3. Backend: Proto Mapper

- [ ] 3.1 Update `go.mod` with new BSR-generated proto (after step 0.4)
- [ ] 3.2 Add `logoColorProfileToProto` function in `mapper/artist.go`
- [ ] 3.3 Call `logoColorProfileToProto` from `fanartToProto` when `f.LogoColorProfile != nil`
- [ ] 3.4 Unit test mapper: fanart with LogoColorProfile → proto has logo_color_profile field, fanart without → proto has no logo_color_profile

## 4. Frontend: Background Color Derivation

- [ ] 4.1 Update `follow-service-client.ts`: map `artist.fanart.logoColorProfile` fields to `FollowedArtistInfo` (`dominantHue?`, `dominantLightness?`, `isChromatic?`)
- [ ] 4.2 Update `color-generator.ts`: add `artistHueFromColorProfile(profile, artistName)` that returns `dominantHue` when present (chromatic), name-hash when absent (achromatic)
- [ ] 4.3 Update `artist-color` custom attribute to accept optional `LogoColorProfile` data and set `--artist-hue` and `--artist-bg-lightness` custom properties
- [ ] 4.4 Update CSS to use `--artist-bg-lightness` for unmatched card backgrounds when available
- [ ] 4.5 Propagate LogoColorProfile through `dashboard-service.ts` → `LiveEvent` → `event-card`

## 5. Verification

- [ ] 5.1 Run `make check` in backend
- [ ] 5.2 Run `make check` in frontend
- [ ] 5.3 Visual verification: chromatic logos (e.g., Suchmos) have logo-hue-family backgrounds
- [ ] 5.4 Visual verification: achromatic dark logos (e.g., SPYAIR) have raised-lightness backgrounds
- [ ] 5.5 Visual verification: achromatic light logos (e.g., UVERworld) retain dark backgrounds with colorful hues
- [ ] 5.6 Visual verification: artists without fanart still use name-hash coloring (no regression)
