#!/usr/bin/env bash
# exit on error
set -o errexit

# install dependencies
pip install -r requirements.txt

# collect static files
python manage.py collectstatic --no-input

# run database migrations
python manage.py makemigrations gigs
python manage.py migrate