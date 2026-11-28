## ADDED Requirements

### Requirement: Create stores the known names
Create SHALL register each new artist with the known names it was given, adding its name when it is missing. An artist already registered keeps its known names.

#### Scenario: New artist with aliases
- **WHEN** Create registers an artist given with its name and an alias among its known names
- **THEN** ListByKnownNames finds it by either

#### Scenario: New artist without aliases
- **WHEN** Create registers an artist given with a name and no known names
- **THEN** it is registered with its name as its only known name

#### Scenario: Already registered
- **WHEN** Create is called with an artist that is already registered and different known names
- **THEN** the registered artist keeps its known names
