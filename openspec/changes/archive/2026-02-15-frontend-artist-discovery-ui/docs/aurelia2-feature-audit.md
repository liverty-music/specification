# Aurelia 2 Feature Audit — Artist Discovery UI

## Purpose

This document records the results of auditing the `frontend-artist-discovery-ui` implementation against Aurelia 2's feature set. The goal is to identify where we underuse framework capabilities and where refinements would improve idiomatic correctness, maintainability, or developer experience.

**Reference:** [Aurelia 2 Official Documentation](https://docs.aurelia.io)

---

## Feature Utilization Map

| Feature                          | Used?         | Notes                                            |
|----------------------------------|---------------|--------------------------------------------------|
| DI (`resolve`, `createInterface`)| Well used     | All services + logger follow the pattern          |
| `@bindable`                      | Basic         | No change callbacks (`propertyChanged`)           |
| Lifecycle hooks                  | Partial       | Only `attached`, `detaching`, `loading`           |
| `.call` binding                  | Used (legacy) | Should migrate to `CustomEvent` + `.trigger`      |
| `@watch`                         | Not used      | Getters are fine for current use case             |
| Value converters                 | Not used      | Minor opportunity for pluralization               |
| Custom attributes                | Not used      | Not needed for this feature                       |
| Event modifiers                  | Not used      | Canvas handles raw events — N/A                   |
| Lambda expressions               | Not used      | Minor template simplification opportunity         |
| `binding` / `bound` hooks        | Not used      | `loading()` handles early init correctly          |
| `propertyChanged` callbacks      | Not used      | Opportunity for orb pulse on follow count change  |
| `au-slot`                        | Not used      | Not needed — no content projection scenario       |
| `IEventAggregator`               | Not used      | Not needed — service DI is sufficient             |
| `INode` injection                | Not used      | Needed for idiomatic `CustomEvent` dispatch       |

---

## Findings — Prioritized

### 1. `.call` binding should be replaced with `CustomEvent` + `.trigger` (HIGH)

**Current pattern:**

```typescript
// dna-orb-canvas.ts — child component
@bindable public artistSelected: ((event: { $event: unknown }) => void) | undefined
// ...
this.artistSelected?.({ $event: artist })
```

```html
<!-- artist-discovery-page.html — parent template -->
<dna-orb-canvas artist-selected.call="onArtistSelected($event)">
```

**Problems:**
- `.call` is an Aurelia 1 compatibility pattern, not idiomatic Aurelia 2
- The `{ $event: artist }` wrapper is a workaround, not a natural API
- The `@bindable` callback type is fragile and poorly typed
- No event bubbling — breaks if component nesting deepens

**Aurelia 2 idiomatic pattern:**

```typescript
// dna-orb-canvas.ts
import { INode } from 'aurelia'

private readonly element = resolve(INode) as HTMLElement

private handleInteraction(x: number, y: number): void {
  // ... physics removal, absorption start ...
  this.element.dispatchEvent(
    new CustomEvent('artist-selected', {
      bubbles: true,
      detail: { artist },
    })
  )
}
```

```html
<!-- artist-discovery-page.html -->
<dna-orb-canvas
  followed-count.bind="followedCount"
  artist-selected.trigger="onArtistSelected($event)"
>
```

```typescript
// artist-discovery-page.ts
public async onArtistSelected(event: CustomEvent<{ artist: ArtistBubble }>): Promise<void> {
  const artist = event.detail.artist
  // ...
}
```

**Benefits:**
- Standard DOM events — bubbles naturally through the component tree
- Clean TypeScript types via `CustomEvent<T>` generic
- Removes the `@bindable` callback hack entirely
- Consistent with Aurelia 2 documentation's recommended approach

**Reference:** [Aurelia 2 Event Binding — Custom Events](https://docs.aurelia.io/templates/overview/event-binding)

---

### 2. `INode` injection for host element access (HIGH)

Required for Finding #1 and idiomatic in general. Aurelia 2 provides `INode` via DI to access the host element of a custom element:

```typescript
import { INode } from 'aurelia'
private readonly element = resolve(INode) as HTMLElement
```

This replaces ad-hoc element access and enables `dispatchEvent` for parent-child communication.

---

### 3. `@bindable` change callbacks — `followedCountChanged` (MEDIUM)

`dna-orb-canvas.ts` declares `@bindable public followedCount = 0` but never reacts to changes. Aurelia 2 automatically calls `[property]Changed(newVal, oldVal)` when a `@bindable` updates:

```typescript
@bindable public followedCount = 0

public followedCountChanged(newVal: number, oldVal: number): void {
  // Trigger orb pulse animation when a new artist is followed
}
```

**Note:** Change callbacks do not fire on initial component creation — they fire only on subsequent updates. To trigger on mount, call the handler manually in `bound()`.

---

### 4. `@watch` decorator for derived state (LOW)

`artist-discovery-page.ts` uses getter properties:

```typescript
public get followedCount(): number {
  return this.discoveryService.followedArtists.length
}
```

The `@watch` decorator could observe deep service state and trigger side effects:

```typescript
@watch((page: ArtistDiscoveryPage) => page.discoveryService.followedArtists.length)
public followedArtistsChanged(newCount: number): void {
  // e.g., analytics, logging, conditional logic
}
```

**Assessment:** For this specific case, getters are lightweight and sufficient. `@watch` becomes valuable when there are side effects to trigger beyond template rendering. No change recommended unless analytics or animation triggers are added later.

---

### 5. Value converter for pluralization (LOW)

The template hardcodes English plural:

```html
View Live Schedule (${followedCount} artists)
```

A value converter would handle `"1 artist"` vs `"5 artists"` correctly:

```typescript
@valueConverter('pluralize')
export class PluralizeValueConverter {
  toView(count: number, singular: string, plural?: string): string {
    const word = count === 1 ? singular : (plural ?? `${singular}s`)
    return `${count} ${word}`
  }
}
```

```html
View Live Schedule (${followedCount | pluralize:'artist'})
```

**Assessment:** Minor polish. Useful if the app grows to support localization (i18n), but not critical for MVP.

---

## Features Correctly Used

These are patterns where the implementation already follows Aurelia 2 best practices:

| Pattern | Location | Assessment |
|---------|----------|------------|
| `DI.createInterface` + `resolve()` | All services | Correct singleton registration and injection |
| Convention-based component naming | All `.ts`/`.html` pairs | No need for explicit `@customElement` decorator |
| `@route` decorator with lazy imports | `my-app.ts` | Dynamic `import()` for code splitting |
| `loading()` router lifecycle hook | `artist-discovery-page.ts`, `auth-callback.ts` | Correct async data loading before render |
| `attached()` / `detaching()` | `dna-orb-canvas.ts` | Proper canvas lifecycle (init in attached, cleanup in detaching) |
| `ref="canvas"` for element reference | `dna-orb-canvas.html` | Correct way to get a child element reference |
| `ILogger.scopeTo()` | All components and services | Structured logging with component context |
| `if.bind` conditional rendering | `artist-discovery-page.html` | Correct conditional button display |
| `repeat.for` iteration | `toast-notification.html` | Correct list rendering |

---

## Lifecycle Hooks Reference

For context, the full Aurelia 2 component lifecycle (in order):

```
constructor → define → hydrating → hydrated → created
→ binding → bound → attaching → attached
→ detaching → unbinding → dispose
```

Our implementation uses: `loading` (router), `attached`, `detaching` — which is appropriate for a canvas-based component that needs DOM access. The earlier hooks (`binding`, `bound`) are useful for data setup before DOM is ready, but our data loading happens in the router's `loading()` hook, which runs before child lifecycles start.

---

## Recommendation

**Priority refactor:** Replace `.call` binding with `CustomEvent` + `.trigger` and inject `INode`. This is a small, focused change that aligns the codebase with Aurelia 2's recommended event communication pattern.

**Defer:** `@watch`, value converters, and additional change callbacks — these add marginal value for the current feature scope and can be adopted as the app grows.
