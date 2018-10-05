# PHMI IG Dashboard

## Requirements

This project uses Python 3.7.x and Sass.
You will need [Pipenv](https://pipenv.readthedocs.io/en/latest/) installed, we recommend doing so with [pipsi](https://github.com/mitsuhiko/pipsi) (`pipsi install pipenv`).

## Install

    pipenv install


## Initial Set Up
Migrate your database with:

    pipenv run python manage.py migrate

Load the data dump:

    pipenv run python manage.py loaddata data/db-dump.json


Alternatively you can load the current data from the CSVs:

    pipenv run python manage.py add_org_types data/csvs/org-types.csv
    pipenv run python manage.py add_group_types data/csvs/group-types.csv
    pipenv run python manage.py add_orgs data/csvs/acute-trust.csv
    pipenv run python manage.py add_orgs data/csvs/ambulance-trust.csv
    pipenv run python manage.py add_orgs data/csvs/ccg.csv
    pipenv run python manage.py add_orgs data/csvs/csu.csv
    pipenv run python manage.py add_orgs data/csvs/community.csv
    pipenv run python manage.py add_orgs data/csvs/dscro.csv
    pipenv run python manage.py add_orgs data/csvs/independent-sector.csv
    pipenv run python manage.py add_orgs data/csvs/local-authority.csv
    pipenv run python manage.py add_orgs data/csvs/mental-health-trust.csv

Note: the `add_orgs` command will ask which OrgType a given set of Organisations is, the filename should be enough to work that out.


## Running

    pipenv run python manage.py runserver
    sass --watch phmi/static/css/styles.scss:phmi/static/css/styles.css


## Notes
Currently this just has an NHS England skin as used by [NCDR](https://data.england.nhs.uk/ncdr/database)
