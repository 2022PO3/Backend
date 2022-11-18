from src.api.serializers.garages.prices_serializer import (
    GetPricesSerializer,
    PostPricesSerializer,
)

from src.api.serializers.garages.locations_serializer import LocationsSerializer
from src.api.serializers.garages.garage_settings_serializer import (
    PostGarageSettingsSerializer,
    GetGarageSettingsSerializer,
)

from src.api.serializers.garages.garages_serializer import (
    GetGaragesSerializer,
    PostGaragesSerializer,
)

from src.api.serializers.garages.opening_hours_serializer import (
    GetOpeningHoursSerializer,
    PostOpeningHoursSerializer,
)

from src.api.serializers.licence_plates_serializer import (
    LicencePlatesSerializer,
    PostLicencePlateSerializer,
)

from src.api.serializers.parking_lots_serializer import ParkingLotsSerializer

from src.api.serializers.users.users_serializer import (
    GetUsersSerializer,
    SignUpSerializer,
    LoginSerializer,
)
from src.api.serializers.users.reservations_serializer import (
    GetReservationsSerializer,
    PostReservationsSerializer,
)
