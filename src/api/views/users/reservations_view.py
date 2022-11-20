from src.core.views import  BaseAPIView
from src.api.models import Reservation
from src.api.serializers import PostReservationSerializer, GetReservationSerializer


class GetReservationsView(BaseAPIView):
    """
    A view class to get all reservations from the currently logged in user.
    """

    origins = ["app", "web"]
    serializer = GetReservationSerializer
    get_user_id = True
    model = Reservation


class PostReservationsView(BaseAPIView):
    """
    A view class to post new reservations for the currently logged in user.
    """

    origins = ["app", "web"]
    serializer = PostReservationSerializer
    post_user_id = True
    model = Reservation
