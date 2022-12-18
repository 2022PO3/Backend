from src.api.views.garages.garage_view import GaragesDetailView, GaragesListView
from src.api.views.garages.opening_hours_view import (
    OpeningHoursGarageView,
    OpeningHoursDetailView,
)
from src.api.views.garages.prices_view import PricesDetailView, PricesGarageView
from src.api.views.garages.parking_lots_view import (
    ParkingLotsGarageView,
    ParkingLotDetailView,
    ParkingLotRPiView,
    ParkingLotAssignView,
)
from src.api.views.licence_plates.licence_plate_view import LicencePlateDetailView

from src.api.views.users.user_view import (
    UserDetailView,
    UserActivationView,
    ChangePasswordView,
)
from src.api.views.users.reservations_view import (
    ReservationsListView,
    ReservationsDetailView,
    ReservationsRPiView,
)

from src.api.views.auth.login_view import LoginView
from src.api.views.auth.logout_view import LogoutView
from src.api.views.auth.sign_up_view import SignUpView

from src.api.views.licence_plates.licence_plate_image_view import LicencePlateImageView

from src.api.views.auth.multi_factor.totp_view import (
    TOTPVerifyView,
    TOTPDetailView,
    TOTPListView,
    Disable2FAView,
)


from src.api.views.payment.checkout_preview_view import (
    CheckoutPreviewView,
)
from src.api.views.payment.checkout_session_view import CheckoutSessionSerializer
from src.api.views.payment.checkout_webhook_view import CheckoutWebhookView

from src.api.views.users.notifications_view import (
    NotificationsListView,
    NotificationsDetailView,
)
