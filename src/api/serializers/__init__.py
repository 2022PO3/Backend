from src.api.serializers.garages.price_serializer import (
    PriceSerializer,
)

from src.api.serializers.garages.location_serializer import LocationsSerializer
from src.api.serializers.garages.garage_settings_serializer import (
    GarageSettingsSerializer,
)

from src.api.serializers.garages.garage_serializer import GarageSerializer

from src.api.serializers.garages.opening_hour_serializer import OpeningHourSerializer

from src.api.serializers.licence_plate_serializer import (
    LicencePlateSerializer,
    PostLicencePlateSerializer,
)

from src.api.serializers.garages.parking_lot_serializer import (
    ParkingLotSerializer,
    RPIParkingLotSerializer,
)

from src.api.serializers.users.users_serializer import (
    UsersSerializer,
    SignUpSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
)
from src.api.serializers.users.reservation_serializer import (
    GetReservationSerializer,
    PostReservationSerializer,
    AssignReservationSerializer,
)
from src.api.serializers.users.totp_serializer import (
    GetTOTPSerializer,
    PostTOTPSerializer,
)
