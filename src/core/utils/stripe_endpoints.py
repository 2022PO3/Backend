from os import getenv

import stripe

from src.api.models import Garage

stripe.api_key = getenv("STRIPE_SECRET_KEY")
publishableKey = getenv("STRIPE_PUBLISHABLE_KEY")


def get_stripe_price(price_id) -> stripe.Price:
    return stripe.Price.retrieve(price_id)


def create_stripe_price(price_data, garage_id: int) -> stripe.Price:
    return stripe.Price.create(
        currency=price_data["valuta"],
        unit_amount=int(price_data["price"] * 100),
        nickname=price_data["price_string"],
        product_data={
            "name": price_data["price_string"]
        },
    )
