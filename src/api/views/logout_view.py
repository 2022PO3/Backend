from django.contrib.auth.signals import user_logged_out

from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


class LogoutView(APIView):
    """
    View to log out the currently logged in user.

    It takes in an empty POST-request with an authentication header and logs out the current user, which means that the auth_token is deleted.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, format=None) -> Response:
        request._auth.delete()
        user_logged_out.send(
            sender=request.user.__class__, request=request, user=request.user
        )
        return Response(None, status=status.HTTP_204_NO_CONTENT)
