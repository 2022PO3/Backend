#!/bin/bash
echo "Starting up Django and waiting 30s"
sleep 30s
echo "Migrating database..."
python manage.py migrate
echo "Seeding database..."
echo "Seed users"
python manage.py loaddata src/api/fixtures/users_fixture.json
echo "Seed Garages"
python manage.py loaddata src/api/fixtures/garages_fixture.json
echo "Seed parking lots"
python manage.py loaddata src/api/fixtures/parking_lots_fixture.json
echo "Migrations and seeding completed. Starting up server..."
gunicorn src.core.wsgi:application -b 0.0.0.0:8000 --reload
