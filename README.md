# PHMI IG Dashboard

## Requirements

This project uses Python 3.7.x and Sass.
You will need [Pipenv](https://pipenv.readthedocs.io/en/latest/) installed, we recommend doing so with [pipsi](https://github.com/mitsuhiko/pipsi) (`pipsi install pipenv`).

## Install

    pipenv install


## Initial Set Up
Migrate your database with:

    pipenv run python manage.py migrate

Load the initial data:
    pipenv run python manage.py add_org_types data/csvs/org-types.csv
    pipenv run python manage.py add_group_types data/csvs/group-types.csv
    pipenv run python manage.py add_orgs
    pipenv run python manage.py load_care_groups
    pipenv run python manage.py load_activities

Note: the `add_orgs` command will ask which OrgType a given set of Organisations is, the filename should be enough to work that out.


## Running

    pipenv run python manage.py runserver
    sass --watch phmi/static/css/styles.scss:phmi/static/css/styles.css


## deployment
update hosts.dev (and use keys natch)
set your branch in deployment/group_vars/all

```
cd deployment
ansible-playbook setup-server.yml -i hosts.dev
```

## restore
Get the file name you want to restore from S3

```
cd deployment
ansible-playbook restore-server.yml -i hosts.dev --vault-password-file ~/.vault.txt --extra-vars "BUCKET_NAME={{ YOUR BUCKET NAME FROM S3 }}"
```

group_vars/all should contain the following vars
```
#### Project
PROJECT_NAME: # the name of the project.
PROJECT_PATH: # the directory that we download the code to
GIT_REPO: # https git remo download name
LOG_DIR: # the directory of the logs
SECRET_KEY: # the secret key for django

#### Git
GIT_REPO: # https git remo download name
GIT_BRANCH: # the git branch

#### Database
DB_USER: # the post gres user.
DB_NAME: # the post gres database
DB_PASSWORD: # the post gres database password

The created output should look something like

{{ PROJECT PATH }}/{{ PROJECT_NAME }}/ manage.py/wsgi etc
{{ PROJECT_PATH }}/static
{{ LOG_DIR }}/{{ PROJECT_NAME }}.error.log


#### Backups
BACK_UPS_DIR: # the local copy of where we store backups
AWS_BUCKET_NAME: # the AWS back up were we are backing up to
AWS_ACCESS_KEY_ID: # AWS config
AWS_SECRET_ACCESS_KEY: # AWS config
```

to edit the group_vars/all use
```
ansible-vault edit all --vault-password-file ~/.vault.txt
```


## Notes
Currently this just has an NHS England skin as used by [NCDR](https://data.england.nhs.uk/ncdr/database)
