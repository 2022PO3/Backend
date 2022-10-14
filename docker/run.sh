#!/bin/bash
echo "Starting up Django and waiting 30s"
sleep 30s
echo "Migrating database..."
python manage.py migrate
echo "Migrations completed. Starting up server..."
python manage.py runserver 0.0.0.0:8000
