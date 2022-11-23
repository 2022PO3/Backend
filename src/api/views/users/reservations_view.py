from src.core.views import BaseAPIView
from src.api.models import Reservation
from src.api.serializers import GetReservationSerializer, PostReservationSerializer


class ReservationsView(BaseAPIView):
    """
    A view class to get all reservations from the currently logged in user and to post new one.
    The post method is overwritten as a
    """

    origins = ["app", "web"]
    serializer = {"get": GetReservationSerializer, "post": PostReservationSerializer}
    get_user_id = True
    post_user_id = True
    model = Reservation
