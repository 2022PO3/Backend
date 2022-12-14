from src.api.views.garages.garage_view import PkGarageView, ListGarageView
from src.api.views.garages.garage_settings_view import PkGarageSettingsView
from src.api.views.garages.opening_hours_view import (
    PkOpeningHoursView,
    PostOpeningHoursView,
)
from src.api.views.garages.prices_view import PricesView, PkPricesView
from src.api.views.garages.parking_lots_view import (
    ParkingLotView,
    PkParkingLotView,
    RPiParkingLotView,
)
from src.api.views.licence_plates.licence_plate_view import PkLicencePlateView

from src.api.views.users.user_view import (
    UserDetailView,
    UserActivationView,
    ChangePasswordView,
)
from src.api.views.users.reservations_view import (
    ReservationsView,
    PkReservationsView,
    AssignReservationView,
)

from src.api.views.auth.login_view import LoginView
from src.api.views.auth.logout_view import LogoutView
from src.api.views.auth.sign_up_view import SignUpView

from src.api.views.licence_plates.licence_plate_image_view import LicencePlateImageView

from src.api.views.auth.multi_factor.totp_view import (
    TOTPCreateView,
    TOTPVerifyView,
    TOTPDeleteView,
    TOTPView,
    Disable2FA,
)


from src.api.views.payment.checkout_preview_view import (
    CheckoutPreviewView,
)
from src.api.views.payment.checkout_session_view import CheckoutSessionSerializer
from src.api.views.payment.checkout_webhook_view import CheckoutWebhookView

from src.api.views.users.notifications_view import (
    NotificationsView,
    PkNotificationsView,
)
