## 1. Create page-header Custom Element

- [x] 1.1 Create `frontend/src/components/page-header/page-header.ts` with `titleKey` bindable
- [x] 1.2 Create `frontend/src/components/page-header/page-header.html` with `<header>`, `<h1 t.bind="titleKey">`, and `<au-slot>`
- [x] 1.3 Create `frontend/src/components/page-header/page-header.css` with shared styles (grid-area, padding, border, background, h1 typography, flexbox layout)

## 2. Register globally

- [x] 2.1 Import `PageHeader` in `frontend/src/main.ts` and add `.register(PageHeader)`

## 3. Replace route headers

- [x] 3.1 Replace `<header class="[ page-header ]">` in `my-artists-route.html` with `<page-header>` and move action elements into the slot
- [x] 3.2 Remove `.page-header` CSS block from `my-artists-route.css`
- [x] 3.3 Replace `<header class="[ page-header ]">` in `settings-route.html` with `<page-header>`
- [x] 3.4 Remove `.page-header` CSS block from `settings-route.css`
- [x] 3.5 Replace `<header class="[ page-header ]">` in `tickets-route.html` with `<page-header>`
- [x] 3.6 Remove `.page-header` CSS block from `tickets-route.css`

## 4. Verify

- [x] 4.1 Run `make check` to ensure lint, typecheck, and tests pass
