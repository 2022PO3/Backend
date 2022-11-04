from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request

from rest_framework.views import APIView


class SignUpView(APIView):
    def post(self, request: Request, format=None) -> Response:
