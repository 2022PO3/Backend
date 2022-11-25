from src.core.views import PkAPIView, BaseAPIView
from src.api.models import Price
from src.api.serializers import PriceSerializer
from src.users.permissions import IsGarageOwner


class PricesView(PkAPIView):
    """
    A view class which renders all the prices for a given garage with `pk`.
    """

    origins = ["app", "web"]
    column = "garage_id"
    serializer = PriceSerializer
    model = Price
    list = True


class PostPricesView(BaseAPIView):
    origins: list[str] = ["app", "web"]
    permission_classes = [IsGarageOwner]
    serializer = {"post": PriceSerializer}
    model = Price 
