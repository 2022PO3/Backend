#!/bin/bash
for file in $(pwd)/src/api/seeds/fixtures/*
do  
    echo "Seeding $(basename $file)"
    python manage.py loaddata $file
done
