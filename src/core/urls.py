"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, re_path
from src.api.views import (
    PkGarageView,
    ListGarageView,
    PkLicencePlateView,
    UserDetailView,
    UserActivationView,
    PkGarageSettingsView,
    ReservationsView,
    PkOpeningHoursView,
    PostOpeningHoursView,
    ParkingLotView,
    PkParkingLotView,
    RPiParkingLotView,
    AssignReservationView,
    PkReservationsView,
    PkPricesView,
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
    NotificationsView,
    PkNotificationsView,
)
from src.api.views.garages.garage_view import OwnedGarageListView
from src.api.views.garages.prices_view import GaragePricesView
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


urlpatterns = [
    path("api/garage/<int:pk>", PkGarageView.as_view()),
    path("api/garages", ListGarageView.as_view()),
    path("api/user/garages/", OwnedGarageListView.as_view()),
    path("api/parking-lots/<int:pk>", ParkingLotView.as_view()),
    path("api/parking-lot/<int:pk>", PkParkingLotView.as_view()),
    path("api/assign-parking-lot/<int:pk>", AssignReservationView.as_view()),
    path("api/user", UserDetailView.as_view()),
    path("api/licence-plate/<int:pk>", PkLicencePlateView.as_view()),
    path("api/licence-plates", LicencePlateListView.as_view()),
    path("api/garage-settings/<int:pk>", PkGarageSettingsView.as_view()),
    path("api/reservations", ReservationsView.as_view()),
    path("api/reservation/<int:pk>", PkReservationsView.as_view()),
    path("api/opening-hours/<int:pk>", PkOpeningHoursView.as_view()),
    path("api/opening-hours", PostOpeningHoursView.as_view()),
    path("api/prices/<int:pk>", PkPricesView.as_view()),
    path("api/garage/prices/<int:pk>", GaragePricesView.as_view()),
    path("api/user/change-password", ChangePasswordView.as_view()),
    path("api/notifications", NotificationsView.as_view()),
    path("api/notification/<int:pk>", PkNotificationsView.as_view()),
]

# User authentication
urlpatterns += [
    path("api/auth/login", LoginView.as_view()),  # type: ignore
    path("api/auth/logout", LogoutView.as_view()),  # type: ignore
    path("api/auth/sign-up", SignUpView.as_view()),  # type: ignore
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

# Raspberry Pi
urlpatterns += [
    path("api/images", LicencePlateImageView.as_view()),
    path("api/rpi-parking-lot", RPiParkingLotView.as_view()),
]

# Payment
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
