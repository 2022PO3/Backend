from django.contrib.auth.signals import user_logged_out

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from src.core.views import _OriginAPIView


class LogoutView(_OriginAPIView):
    """
    View to log out the currently logged in user.

    It takes in an empty POST-request with an authentication header and logs out the current user, which means that the auth_token is deleted.
    """

    origins = ["web", "app"]
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> Response:
        if (resp := super().post(request, format)) is not None:
            return resp
        request._auth.delete()
        request.user.two_factor_validated = False
        request.user.save()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )
        return Response(None, status=status.HTTP_204_NO_CONTENT)
