#!/bin/bash
rm src/api/seeds/fixture/*
python src/api/seeds/create_fixtures.py
for file in $(pwd)/src/api/seeds/fixtures/*
do  
    echo "Seeding $(basename $file)"
    python manage.py loaddata $file
done
