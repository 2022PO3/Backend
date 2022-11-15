#!/bin/bash
echo "Starting up Django and waiting 10s"
sleep 10s

echo "Migrating database..."
python manage.py makemigrations
python manage.py migrate

echo "Seeding database..."
python src/api/seeds/create_fixtures.py
bash docker/run.sh

echo "Migrations and seeding completed. Starting up server..."
gunicorn src.core.wsgi:application -b 0.0.0.0:8000 --reload
