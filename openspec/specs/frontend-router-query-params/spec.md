# Frontend Router Query Parameters

## Purpose

Define the canonical pattern for reading URL query parameters in Aurelia 2 route lifecycle hooks. Route `loading()` hooks SHALL use `RouteNode.queryParams` rather than `window.location.search` to decouple from the live browser URL and enable pure unit testing.

## Requirements

### Requirement: Route loading hooks read query parameters via RouteNode
Route `loading()` lifecycle hooks SHALL read URL query parameters from `next.queryParams` (a `URLSearchParams` instance provided by Aurelia Router) rather than `window.location.search`, so that the parameter source is injectable and not coupled to the live browser URL.

#### Scenario: Query params are read from RouteNode in loading()
- **WHEN** `loading(_params, next)` is called with a `RouteNode` whose `queryParams` contains `title` and `text`
- **THEN** the route SHALL read `title` and `text` from `next.queryParams` without accessing `window.location`

#### Scenario: Test can inject query params without mutating window.location
- **WHEN** a unit test calls `loading({}, { queryParams: new URLSearchParams('title=T&text=チケット') })`
- **THEN** the route SHALL parse those params correctly, and the test SHALL NOT require `window.history.replaceState`

#### Scenario: Missing query params default to empty string
- **WHEN** `next.queryParams` does not contain `title` or `text`
- **THEN** `emailTitle` and `emailBody` SHALL default to `''`
