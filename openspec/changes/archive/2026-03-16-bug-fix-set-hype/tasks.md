## 1. Component: hype-inline-slider

- [x] 1.1 Change `@bindable hypeLevel: HypeStop` to `@bindable hype: HypeType` in `hype-inline-slider.ts`
- [x] 1.2 Replace `stops` array from `HypeStop[]` to `HypeType[]` (`[HypeType.WATCH, HypeType.HOME, HypeType.NEARBY, HypeType.AWAY]`)
- [x] 1.3 Update `selectHype()` to dispatch `hype-changed` with `{ artistId, hype: HypeType }` detail
- [x] 1.4 Remove the `HypeStop` type export from `hype-inline-slider.ts`
- [x] 1.5 Update `hype-inline-slider.html`: add `role="radiogroup"` + `aria-label` to container, `role="radio"` + `aria-checked` to buttons
- [x] 1.6 Update `hype-inline-slider.html`: change `data-active` and `data-level` bindings to use `HypeType` values
- [x] 1.7 Update `hype-inline-slider.css`: change `data-level` selectors from string names (`"watch"`, `"home"`, etc.) to enum values (`"1"`, `"2"`, `"3"`, `"4"`)

## 2. Route: my-artists-route

- [x] 2.1 Remove `HypeStop` import, `HYPE_TO_STOP`, `HYPE_FROM_STOP`, and `hypeStop()` method from `my-artists-route.ts`
- [x] 2.2 Update `onHypeChanged()` to read `HypeType` from event detail directly (no `HYPE_FROM_STOP` conversion)
- [x] 2.3 Update `my-artists-route.html`: change `hype-level.bind="hypeStop(artist)"` to `hype.bind="artist.hype"`
- [x] 2.4 Update `my-artists-route.html`: remove `hype-inline-slider` import alias if `HypeStop` type import was part of it

## 3. Tests

- [x] 3.1 Update `hype-inline-slider.spec.ts`: replace `HypeStop` references with `HypeType`, update event detail assertions
- [x] 3.2 Update `my-artists-route.spec.ts`: remove `hypeStop()` tests, update `onHypeChanged` test event details
- [x] 3.3 Run `make check` and verify all tests pass
