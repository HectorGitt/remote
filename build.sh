#!/usr/bin/env bash
# exit on error
set -o errexit


pip freeze > requirements.txt
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py makemigrations gigs
python manage.py migrate