## 1. Proto Documentation

- [x] 1.1 Update `ListTop` RPC comment to document data-source priority logic (tag → geo → chart)
- [x] 1.2 Update `ListTopRequest.country` field comment to note it is ignored when `tag` is set
- [x] 1.3 Update `ListTopRequest.tag` field comment to note results are global when tag is specified

## 2. Browser Locale Detection Utility

- [x] 2.1 Create timezone-to-country mapping module in `frontend/src/util/` with IANA timezone → ISO 3166-1 country name table
- [x] 2.2 Export a `detectCountryFromTimezone()` function that returns country name or empty string
- [x] 2.3 Write unit tests for known timezones, unknown timezones, and `Intl` API unavailability

## 3. Discovery Page Integration

- [x] 3.1 Remove hardcoded `'Japan'` from `bubble-manager.ts` — use `detectCountryFromTimezone()` for `private country`
- [x] 3.2 Remove hardcoded `'Japan'` default from `genre-filter-controller.ts` `reloadWithTag()` — use detected country
- [x] 3.3 Remove hardcoded `'Japan'` from `discovery-route.ts` `loading()` — use detected country
- [x] 3.4 Update unit tests in `discovery-route.spec.ts` to mock timezone detection instead of hardcoded `'Japan'`

## 4. Verification

- [x] 4.1 Run `make check` in frontend to verify lint and tests pass
- [x] 4.2 Run `buf lint` and `buf breaking` in specification to verify proto changes
