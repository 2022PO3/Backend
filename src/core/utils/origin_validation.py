import os

from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from src.core.views import BackendResponse


