#!/usr/bin/env bash
# exit on error
set -o errexit

# install dependencies
pip install -r requirements.txt

# collect static files
python manage.py collectstatic --no-input

# build tailwind
export NODE_OPTIONS=--openssl-legacy-provider
npm install -D tailwindcss
python manage.py tailwind build

# run database migrations
python manage.py makemigrations gigs
python manage.py migrate