from src.core.views import PkAPIView
from src.api.models import Price
from src.api.serializers import PriceSerializer


class PricesView(PkAPIView):
    """
    A view class which renders all the prices for a given garage with `pk`.
    """

    origins = ["app", "web"]
    column = "garage_id"
    serializer = PriceSerializer
    model = Price
    list = True
