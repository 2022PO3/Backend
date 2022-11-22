from src.api.views.garages.garage_view import GarageDetailView, GarageListView
from src.api.views.garages.garage_settings_view import GetGarageSettingsView
from src.api.views.garages.opening_hours_view import (
    GetOpeningHoursView,
    PostOpeningHoursView,
)
from src.api.views.garages.prices_view import PricesView
from src.api.views.garages.parking_lots_view import (
    ParkingLotsListView,
    ParkingLotsDetailView,
)
from src.api.views.licence_plate_view import LicencePlateDetailView, RPiLicencePlateView

from src.api.views.users.user_view import UserDetailView
from src.api.views.users.reservations_view import GetReservationsView

from src.api.views.auth.login_view import LoginView
from src.api.views.auth.logout_view import LogoutView
from src.api.views.auth.sign_up_view import SignUpView
