echo "Seed users"
python manage.py loaddata src/api/fixtures/users_fixture.json
echo "Seed Garages"
python manage.py loaddata src/api/fixtures/garages_fixture.json
echo "Seed parking lots"
python manage.py loaddata src/api/fixtures/parking_lots_fixture.json