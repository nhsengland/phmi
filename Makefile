help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make format           run the auto-format check."
	@echo "    make lint             run the import sorter check."
	@echo "    make load-data        load the main database fixture."
	@echo "    make setup            set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: format
format:
	@echo "Running black" && pipenv run black --check phmi projects || exit 1

.PHONY: lint
lint:
	@echo "Running flake8" && pipenv run flake8 --show-source || exit 1

.PHONY: load-data
load-data:
	@pipenv run python manage.py loaddata data/json/db.json

.PHONY: setup
setup:
	pipenv install --dev

.PHONY: sort
sort:
	@echo "Running Isort" && pipenv run isort --check-only --diff || exit 1

.PHONY: test
test:
	pipenv run python manage.py test
