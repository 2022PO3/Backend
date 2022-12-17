from django.urls import path, re_path
from src.api.views import (
    GaragesDetailView,
    GaragesListView,
    LicencePlateDetailView,
    UserDetailView,
    UserActivationView,
    ReservationsListView,
    ReservationsDetailView,
    ReservationsRPiView,
    OpeningHoursGarageView,
    OpeningHoursDetailView,
    ParkingLotsGarageView,
    ParkingLotDetailView,
    ParkingLotRPiView,
    ParkingLotAssignView,
    PricesDetailView,
    PricesGarageView,
    LoginView,
    LogoutView,
    SignUpView,
    ChangePasswordView,
    LicencePlateImageView,
    TOTPVerifyView,
    TOTPCreateView,
    TOTPDeleteView,
    TOTPView,
    Disable2FA,
    NotificationsListView,
    NotificationsDetailView,
)
from src.api.views.garages.prices_view import PricesGarageView
from src.api.views.licence_plates.licence_plate_view import LicencePlateListView
from src.api.views.payment.checkout_preview_view import CheckoutPreviewView
from src.api.views.payment.checkout_session_view import CreateCheckoutSessionView
from src.api.views.payment.checkout_webhook_view import CheckoutWebhookView
from src.api.views.payment.invoice_webhook_view import InvoiceWebhookView
from src.api.views.payment.send_invoice_view import SendInvoiceView
from src.api.views.payment.user_stripe_connection_view import UserStripeConnectionView
from src.core.settings import DEBUG

handler404 = "src.core.views.not_found_error"
handler500 = "src.core.views.server_error"

"""
By convention, the routes should be build in the following way: 
    - routes for getting, editing or deleting a single object are of the form `api/object/<int:pk>`; note the singular form of object.
    - routes for getting multiple objects or for posting a new one are of the form `api/objects`; note the plural form of objects.
    - routes for getting, posting, editing or deleting an object based on the `pk` of another object (e.g. getting a location based on the `garage_pk`) are of the form `api/object/<int:other_object_pk>`; note the singular form of object.
    - routes for getting multiple object based on the `pk` of another object or posting a new one (e.g. getting all the prices based on a `garage_pk`) are of the form `api/objects/<int:other_object_pk>`; note the plural form of objects.
"""
###############
# Garage URLs #
###############
# Garages
urlpatterns = [
    path("api/garage/<int:pk>", GaragesDetailView.as_view()),
    path("api/garages", GaragesListView.as_view()),
]

# Parking lots
urlpatterns += [
    path("api/parking-lot/<int:garage_pk>", ParkingLotDetailView.as_view()),  #!
    path("api/parking-lots/<int:garage_pk>", ParkingLotsGarageView.as_view()),
    path("api/assign-parking-lot/<int:garage_pk>", ParkingLotAssignView.as_view()),
]

# Prices
urlpatterns += [
    path("api/price/<int:pk>", PricesDetailView.as_view()),
    path("api/prices/<int:garage_pk>", PricesGarageView.as_view()),  #!
]

# Opening hours
urlpatterns += [
    path("api/opening-hour/<int:pk>", OpeningHoursDetailView.as_view()),
    path("api/opening-hours/<int:garage_pk>", OpeningHoursGarageView.as_view()),
]

#############
# User URLs #
#############
urlpatterns += [
    path("api/user", UserDetailView.as_view()),
    path("api/user/change-password", ChangePasswordView.as_view()),
]

# Reservations
urlpatterns += [
    path("api/reservation/<int:pk>", ReservationsDetailView.as_view()),
    path("api/reservations", ReservationsListView.as_view()),
]

# Licence plates
urlpatterns += [
    path("api/licence-plate/<int:pk>", LicencePlateDetailView.as_view()),
    path("api/licence-plates", LicencePlateListView.as_view()),
]

# Notifications
urlpatterns += [
    path("api/notification/<int:pk>", NotificationsDetailView.as_view()),
    path("api/notifications", NotificationsListView.as_view()),
]


##################
# Authentication #
##################
urlpatterns += [
    path("api/auth/login", LoginView.as_view()),
    path("api/auth/logout", LogoutView.as_view()),
    path("api/auth/sign-up", SignUpView.as_view()),
    path(
        "api/auth/activate-account/<str:uid_b64>/<str:token>",
        UserActivationView.as_view(),
    ),
    path("api/auth/totp/create", TOTPCreateView.as_view()),
    re_path(r"^api/auth/totp/login/(?P<token>[0-9]{6})$", TOTPVerifyView.as_view()),
    path("api/auth/totp/<int:pk>", TOTPDeleteView.as_view()),
    path("api/auth/totp", TOTPView.as_view()),
    path("api/auth/totp/disable", Disable2FA.as_view()),
]


################
# Raspberry Pi #
################
urlpatterns += [
    path("api/images", LicencePlateImageView.as_view()),
    path("api/rpi-parking-lot", ParkingLotRPiView.as_view()),
    path("api/reservations/<int:garage_pk>", ReservationsRPiView.as_view()),
]


###########
# Payment #
###########
urlpatterns += [
    path("api/checkout/create-session", CreateCheckoutSessionView.as_view()),
    path("api/checkout/preview", CheckoutPreviewView.as_view()),
    path("api/checkout/webhook", CheckoutWebhookView.as_view()),
    path("api/stripe-connection", UserStripeConnectionView.as_view()),
    path("api/invoice/webhook", InvoiceWebhookView.as_view()),
]

if DEBUG:
    urlpatterns += [
        path("api/send-invoice", SendInvoiceView.as_view()),
    ]
