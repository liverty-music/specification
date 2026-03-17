## 0. Specification: Proto Schema

- [ ] 0.1 Add `LogoAnalysis` message to `artist.proto` with `dominant_hue` (float), `dominant_lightness` (float), `is_chromatic` (bool)
- [ ] 0.2 Add `optional LogoAnalysis logo_analysis = 6` field to the `Fanart` message
- [ ] 0.3 Run `buf lint` and `buf format -w`
- [ ] 0.4 Create specification PR, merge, create release → BSR publishes

## 1. Backend: Color Extraction (Entity Layer)

- [ ] 1.1 Add `LogoAnalysis` struct to `entity/fanart.go` with `DominantHue float64`, `DominantLightness float64`, `IsChromatic bool` and JSON tags
- [ ] 1.2 Add `LogoAnalysis *LogoAnalysis` field to `Fanart` struct with `json:"logoAnalysis,omitempty"` tag
- [ ] 1.3 Implement `oklch.go` in `entity/` with sRGB→LinearRGB→OKLab→OKLCH conversion (pure math, no external deps)
- [ ] 1.4 Unit test `oklch.go`: pure white → L≈1.0 C≈0.0, pure red → L≈0.63 C>0.2 H≈29°, pure black → L≈0.0 C≈0.0
- [ ] 1.5 Implement `AnalyzeLogo(img image.Image) *LogoAnalysis` in `entity/fanart.go`: skip transparent pixels, build hue histogram, classify chromatic/achromatic, return analysis
- [ ] 1.6 Unit test `AnalyzeLogo`: chromatic image (>30% colored pixels), achromatic light image, achromatic dark image, fully transparent image → nil

## 2. Backend: Sync Pipeline Integration

- [ ] 2.1 Add `DownloadAndAnalyzeLogo(ctx, fanart *Fanart) *LogoAnalysis` to the image sync use case: select best logo URL (HDMusicLogo → MusicLogo fallback), HTTP GET, `image/png` decode, call `AnalyzeLogo`
- [ ] 2.2 Update `SyncArtistImages` (CronJob path) to call `DownloadAndAnalyzeLogo` and set `fanart.LogoAnalysis` before persisting
- [ ] 2.3 Update ARTIST.created consumer to call `DownloadAndAnalyzeLogo` after fetching fanart data
- [ ] 2.4 Handle logo download failures gracefully: log warning, proceed with nil LogoAnalysis (non-fatal)
- [ ] 2.5 Run `make check` in backend

## 3. Backend: Proto Mapper

- [ ] 3.1 Update `go.mod` with new BSR-generated proto (after step 0.4)
- [ ] 3.2 Add `logoAnalysisToProto` function in `mapper/artist.go`
- [ ] 3.3 Call `logoAnalysisToProto` from `fanartToProto` when `f.LogoAnalysis != nil`
- [ ] 3.4 Unit test mapper: fanart with LogoAnalysis → proto has logo_analysis field, fanart without → proto has no logo_analysis

## 4. Frontend: Background Color Derivation

- [ ] 4.1 Update `follow-service-client.ts`: map `artist.fanart.logoAnalysis` fields to `FollowedArtistInfo` (`dominantHue?`, `dominantLightness?`, `isChromatic?`)
- [ ] 4.2 Update `color-generator.ts`: add `artistHueFromAnalysis(analysis, artistName)` that returns analysis-driven hue for chromatic logos, name-hash for achromatic
- [ ] 4.3 Update `artist-color` custom attribute to accept optional `LogoAnalysis` data and set `--artist-hue` and `--artist-bg-lightness` custom properties
- [ ] 4.4 Update CSS to use `--artist-bg-lightness` for unmatched card backgrounds when available
- [ ] 4.5 Propagate LogoAnalysis through `dashboard-service.ts` → `LiveEvent` → `event-card`

## 5. Verification

- [ ] 5.1 Run `make check` in backend
- [ ] 5.2 Run `make check` in frontend
- [ ] 5.3 Visual verification: chromatic logos (e.g., Suchmos) have logo-hue-family backgrounds
- [ ] 5.4 Visual verification: achromatic dark logos (e.g., SPYAIR) have raised-lightness backgrounds
- [ ] 5.5 Visual verification: achromatic light logos (e.g., UVERworld) retain dark backgrounds with colorful hues
- [ ] 5.6 Visual verification: artists without fanart still use name-hash coloring (no regression)
