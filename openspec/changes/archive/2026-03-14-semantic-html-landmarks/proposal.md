# Semantic HTML & Landmarks

## Problem

The frontend templates use generic `<div>` elements where semantic HTML5 elements are appropriate. This causes:

- Screen readers cannot identify page regions (no `<main>`, `<header>`, `<aside>` landmarks)
- Browser accessibility tree is flat and uninformative
- CUBE CSS bracket notation (`class="[ block ]"`) is missing from nearly all templates, violating the project's CSS methodology
- ARIA labels are missing from dialogs, status regions, and interactive elements
- Date/time values use plain text instead of `<time>` elements

## Proposed Solution

Systematic pass through all 28 HTML templates to:

1. Replace `<div class="*-layout">` with `<main>` on all route pages
2. Replace structural divs with `<header>`, `<nav>`, `<aside>`, `<article>`, `<section>`, `<footer>` where semantically correct
3. Apply CUBE CSS bracket notation to all class attributes
4. Add missing ARIA attributes (`aria-labelledby` on dialogs, `aria-live` on status regions)
5. Use `<time>` for dates, `<address>` for venue locations, `<hr>` for decorative dividers

## Scope

- **In scope**: HTML template changes only. One CSS selector update in `my-app.css` (`main` → `.app-viewport`) was required to avoid invalid nested `<main>` landmarks after route pages adopted their own `<main>`. No TypeScript modifications.
- **Out of scope**: DOM flattening (separate change), component extraction (separate change)

## Affected Files

All 28 `.html` files under `src/`, with primary focus on:
- 10 route pages missing `<main>` landmark
- 6 components missing `aria-labelledby` on `<dialog>`
- 24+ files missing CUBE CSS bracket notation

## Risk

Low. Primarily HTML-only changes with no visual impact. One CSS selector update (`my-app.css`) is mechanical with zero visual change. Bracket notation does not affect selector matching.
