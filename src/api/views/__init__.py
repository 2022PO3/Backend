from src.api.views.garages.garage_view import GarageDetailView, GarageListView
from src.api.views.garages.garage_settings_view import GetGarageSettingsView
from src.api.views.garages.opening_hours_view import (
    GetOpeningHoursView,
    PostOpeningHoursView,
)
from src.api.views.garages.prices_view import PricesView, PostPricesView
from src.api.views.garages.parking_lots_view import (
    ParkingLotView,
    ParkingLotPutView,
    RPiParkingLotView,
)
from src.api.views.licence_plates.licence_plate_view import LicencePlateDetailView

from src.api.views.users.user_view import UserDetailView, UserActivationView
from src.api.views.users.reservations_view import (
    ReservationsView,
    AssignReservationView,
)

from src.api.views.auth.login_view import LoginView
from src.api.views.auth.logout_view import LogoutView
from src.api.views.auth.sign_up_view import SignUpView

from src.api.views.licence_plates.licence_plate_image_view import LicencePlateImageView

from src.api.views.auth.multi_factor.totp_view import TOTPCreateView, TOTPVerifyView
