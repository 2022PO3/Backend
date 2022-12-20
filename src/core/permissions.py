from django_otp import user_has_device

from rest_framework.permissions import BasePermission


class IsAuthenticatedAndVerified(BasePermission):
    """
    Global permission to check if a user is both authenticated and verified (if they have 2FA installed on their account).
    """

    message = ""

    def otp_is_verified(self, request):
        user = request.user
        if not user.two_factor_validated and user.two_factor_validated is None:
            return True
        return bool(user.two_factor_validated and user.is_authenticated)

    def has_permission(self, request, view) -> bool:
        if not request.user:
            return False
        elif user_has_device(request.user):
            self.message = "You do not have permission to perform this action until you verify your OTP device."
            return self.otp_is_verified(request)
        else:
            return request.user.is_authenticated
