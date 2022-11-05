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
from django.contrib import admin
from django.urls import path
from src.api.views import (
    garage_view,
    parking_lot_view,
    user_view,
    licence_plate_view,
    login_view,
    sign_up_view,
    logout_view,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/garage/<int:pk>/", garage_view.GarageDetail.as_view()),  # type: ignore
    path("api/garages/", garage_view.GarageList.as_view()),  # type: ignore
    path("api/parking-lots/", parking_lot_view.ParkingLotList.as_view()),  # type: ignore
    path("api/users/", user_view.UserList.as_view()),  # type: ignore
    path("api/licence-plates/", licence_plate_view.LicencePlateList.as_view()),  # type: ignore
    path("api/licence-plate/<int:pk>", licence_plate_view.LicencePlateDetail.as_view()),  # type: ignore
    # Authentication
    path("auth/login", login_view.LoginView.as_view()),  # type: ignore
    path("auth/logout", logout_view.LogoutView.as_view()),  # type: ignore
    path("auth/sign_up", sign_up_view.SignUpView.as_view()),  # type: ignore
]
