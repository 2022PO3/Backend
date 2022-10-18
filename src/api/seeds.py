from django_seed import Seed
from src.api.models.garages import Garages
from src.api.models.parking_lots import ParkingLots

seeder = Seed.seeder()

seeder.add_entity(Garages, 5)
seeder.add_entity(ParkingLots, 100)

inserted_pks = seeder.execute()
