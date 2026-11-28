## ADDED Requirements

### Requirement: Create stores the name keys
Create SHALL register each new artist with the name keys it was given, adding the key of its name when it is missing. An artist already registered keeps its name keys.

#### Scenario: New artist with aliases
- **WHEN** Create registers an artist given with the keys of its name and an alias
- **THEN** ListByNameKeys finds it by either

#### Scenario: New artist without keys
- **WHEN** Create registers an artist given with a name and no name keys
- **THEN** it is registered with the key of its name

#### Scenario: Already registered
- **WHEN** Create is called with an artist that is already registered and different name keys
- **THEN** the registered artist keeps its name keys
