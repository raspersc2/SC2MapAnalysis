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
