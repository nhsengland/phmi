help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make lint             run the import sorter check."
	@echo "    make setup            set up local env for dev."
	@echo "    make test             run the tests."

.PHONY: lint
lint:
	@echo "Running flake8" && pipenv run flake8 --show-source || exit 1

.PHONY: setup
setup:
	pipenv install --dev

.PHONY: test
test:
	pipenv run python manage.py test
