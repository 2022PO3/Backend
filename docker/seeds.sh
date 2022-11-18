#!/bin/bash
cd $(pwd)/src/api/seeds/fixtures
rm -rf !\(0001_users_fixture.json\)
cd ../../../..; python $(pwd)/src/api/seeds/create_fixtures.py
for file in $(pwd)/src/api/seeds/fixtures/*
do
    echo "Seeding $(basename $file)"
    python manage.py loaddata $file
done
