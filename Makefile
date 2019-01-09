help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make lint             run the import sorter check."
	@echo "    make setup            set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: lint
lint:
	@echo "Running flake8" && pipenv run flake8 --show-source || exit 1

.PHONY: setup
setup:
	pipenv install --dev

.PHONY: sort
sort:
	@echo "Running Isort" && pipenv run isort --check-only --diff || exit 1

.PHONY: test
test:
	pipenv run python manage.py test
