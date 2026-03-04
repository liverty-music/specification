.PHONY: lint fix check

## lint: buf lint + format check + breaking change detection (matches CI)
lint:
	buf lint
	buf format -d --exit-code
	buf breaking --against '.git#branch=main'

## fix: auto-fix formatting
fix:
	buf format -w

## check: full local pre-commit check
check: lint
