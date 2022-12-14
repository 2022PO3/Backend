from base64 import urlsafe_b64encode
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string

from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import AllowAny

from src.api.serializers import SignUpSerializer
from src.core.views import BackendResponse, _OriginAPIView, parse_frontend_json
from src.core.settings import EMAIL_HOST_USER
from src.users.models import User
from src.users.backends import EmailVerificationTokenGenerator


class SignUpView(_OriginAPIView):
    """
    General sign up view for new users. An `email`, `password` and `role` have to be
    provided to create a user. The `first_name` and `last_name` fields are optional.
    """

    permission_classes = [AllowAny]
    origins = ["web", "app"]
    http_method_names = ["post"]

    def post(self, request: Request, format=None) -> BackendResponse:
        if (resp := super().post(request, format)) is not None:
            return resp
        user_data = parse_frontend_json(request)
        user_serializer = SignUpSerializer(data=user_data)  # type:ignore
        if user_serializer.is_valid():
            try:
                validated_user_data = user_serializer.validated_data
                user = User.objects.create_user(
                    validated_user_data["email"],  # type: ignore
                    validated_user_data["password"],  # type: ignore
                    validated_user_data["role"],  # type: ignore
                    first_name=user_serializer.data["first_name"],
                    last_name=user_serializer.data["last_name"],
                )
                SignUpView._send_email_verification(user)
                serializer_data = user_serializer.data
                # Do not show the `password_confirmation` in the response of the API.
                serializer_data.pop("password_confirmation")
                return BackendResponse(serializer_data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return BackendResponse(e.error_list, status=status.HTTP_400_BAD_REQUEST)
        return BackendResponse(
            user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def _send_email_verification(user: User) -> None:
        token = EmailVerificationTokenGenerator().make_token(user)
        url = SignUpView._make_url(token, user.pk)
        msg_plain = render_to_string(
            "activate_user_template.txt", {"activation_url": url}
        )
        msg_html = render_to_string(
            "activate_user_template.html", {"activation_url": url}
        )
        send_mail(
            "Activate Your Account",
            msg_plain,
            EMAIL_HOST_USER,
            [user.email],
            html_message=msg_html,
        )

    @staticmethod
    def _make_url(token: str, user_id: int) -> str:
        """
        Generates a url from the token for resetting the password. Note that this will
        generate a link to the Frontend application, which in turn will send a request to
        the Backend. This to prevent direct unauthorized access to the Backend.
        """
        encoded = urlsafe_b64encode(force_bytes(user_id))
        return f"https://po3backend.ddns.net/web/user-activation?uidB64={str(encoded)[2:-1]}&token={token}"
