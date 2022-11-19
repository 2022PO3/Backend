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
from django.urls import path
from src.api.views import (
    GarageDetailView,
    GarageListView,
    RPiLicencePlateView,
    LicencePlateDetailView,
    UserDetailView,
    GarageSettingsView,
    ReservationsView,
    GetOpeningHoursView,
    PostOpeningHoursView,
    ParkingLotsListView,
    ParkingLotsDetailView,
    PricesView,
    LoginView,
    LogoutView,
    SignUpView,
)

handler500 = "src.core.views.server_error"

urlpatterns = [
    path("api/garage/<int:pk>", GarageDetailView.as_view()),
    path("api/garages", GarageListView.as_view()),
    path("api/licence-plates", RPiLicencePlateView.as_view()),
    path("api/parking-lots/<int:pk>", ParkingLotsListView.as_view()),
    path("api/parking-lot/<int:pk>", ParkingLotsDetailView.as_view()),
    path("api/user", UserDetailView.as_view()),
    path("api/licence-plate/<int:pk>", LicencePlateDetailView.as_view()),
    path("api/garage-settings/<int:pk>", GarageSettingsView.as_view()),
    path("api/reservations", ReservationsView.as_view()),
    path("api/opening-hours/<int:pk>", GetOpeningHoursView.as_view()),
    path("api/opening-hours", PostOpeningHoursView.as_view()),
    path("api/prices/<int:pk>", PricesView.as_view()),
]

# User authentication
urlpatterns += [
    path("api/auth/login", LoginView.as_view()),  # type: ignore
    path("api/auth/logout", LogoutView.as_view()),  # type: ignore
    path("api/auth/sign-up", SignUpView.as_view()),  # type: ignore
]
