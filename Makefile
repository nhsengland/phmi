help:
	@echo "Usage:"
	@echo "    make help             prints this help."
	@echo "    make deploy           deploy the site to the current HEAD server."
	@echo "    make dump-data        dump the current database to a JSON fixture."
	@echo "    make format           run the auto-format check."
	@echo "    make lint             run the import sorter check."
	@echo "    make load-data        load the main database fixture."
	@echo "    make setup            set up local env for dev."
	@echo "    make sort             run the linter."
	@echo "    make test             run the tests."

.PHONY: deploy
deploy:
	@(cd deployment; ansible-playbook setup-server.yml -i hosts.dev --vault-password-file .vault.txt)

.PHONY: dump-data
dump-data:
	@pipenv run python manage.py dumpdata phmi projects --indent=2 --exclude=phmi.User > data/json/db.json

.PHONY: format
format:
	@echo "Running black" && pipenv run black --check phmi projects scripts || exit 1

.PHONY: import-csvs
import-csvs:
	@psql -c "DROP DATABASE phmi;"
	@psql -c "CREATE DATABASE phmi;"
	@pipenv run python manage.py migrate
	@pipenv run python manage.py add_org_types
	@pipenv run python manage.py add_orgs
	@pipenv run python manage.py load_justification_details
	@pipenv run python manage.py load_activities_and_justifications
	@pipenv run python manage.py add_group_types
	@pipenv run python manage.py load_care_groups
	@pipenv run python manage.py add_data_types
	@pipenv run python manage.py add_org_functions
	@pipenv run python manage.py add_benefits
	@pipenv run python manage.py add_outputs
	@pipenv run python manage.py link_activities_to_data_types
	@pipenv run python manage.py create_activity_category_groups

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
