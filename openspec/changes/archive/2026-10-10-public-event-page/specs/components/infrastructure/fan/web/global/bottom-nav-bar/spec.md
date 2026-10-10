# Spec Delta

## MODIFIED Requirements

### Requirement: Active tab reflects the displayed route

The bottom navigation bar SHALL highlight exactly the tab whose route is
displayed, and no tab when the displayed route belongs to none. The tabs the
bar offers and the tab that is active SHALL come from the app's route
configuration, so adding or removing a tab is a change to that configuration
alone. A route that belongs to a tab's section without being the tab's own path
SHALL highlight that tab.

#### Scenario: Tab route displayed

- **WHEN** the displayed route is Home, Discover, My Artists, Tickets or
  Settings
- **THEN** that tab SHALL be highlighted and every other tab SHALL NOT be

#### Scenario: Concert deep-link highlights Home

- **WHEN** the displayed route is a concert deep-link (`/concerts/:id`)
- **THEN** the Home tab SHALL be highlighted

#### Scenario: Event page highlights Home

- **WHEN** the displayed route is an Event page (`/events/:id`)
- **THEN** the Home tab SHALL be highlighted

#### Scenario: Route outside every tab

- **WHEN** the displayed route belongs to no tab (for example an order detail
  or a legal document) while the navigation bar is shown
- **THEN** no tab SHALL be highlighted
