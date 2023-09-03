format-black:
	@black .
format-isort:
	@isort .
lint-black:
	@black . --check
lint-isort:
	@isort . --check
lint-flake8:
	@flake8 .

lint: lint-black lint-isort lint-flake8

current-version:
	@semantic-release print-version --current

next-version:
	@semantic-release print-version --next

current-changelog:
	@semantic-release changelog --released

next-changelog:
	@semantic-release changelog --unreleased

publish-noop:
	@semantic-release publish --noop
