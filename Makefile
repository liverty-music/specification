.PHONY: lint breaking fix words check

## lint: buf lint + format check. Breaking change detection is `make breaking`:
## an intended breaking change passes CI with the `buf skip breaking` label,
## which a local pre-commit gate cannot see, so it is not part of lint.
lint:
	buf lint
	buf format -d --exit-code

## breaking: breaking change detection against origin/main (CI runs it on
## every PR unless the `buf skip breaking` label is applied)
breaking:
	buf breaking --against '.git#branch=origin/main'

## fix: auto-fix formatting
fix:
	buf format -w

## words: reject words no entity defines (tenant, operator, seller, buyer,
## applicant) in proto/, docs/, openspec/specs/ and openspec/schemas/
words:
	python3 scripts/check-forbidden-words.py

## check: full local pre-commit check
check: lint words
