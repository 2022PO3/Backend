from os import getenv

import stripe

from src.api.models.garages.garage import Garage

stripe.api_key = getenv('STRIPE_SECRET_KEY')
publishableKey = getenv('STRIPE_PUBLISHABLE_KEY')


def get_stripe_price(price_id) -> stripe.Price:
    return stripe.Price.retrieve(price_id)


def update_stripe_price(price_data) -> stripe.Price:
    return stripe.Price.modify(
        price_data['stripe_identifier'],
        currency=price_data['valuta'],
        unit_amount=price_data['price'] * 100,
        nickname=price_data['price_string'],
        product_data={
            'name': f'{price_data["duration"]} at {Garage.objects.get(garage_id=price_data["garage_id"]).name}'
        }
    )


def create_stripe_price(price_data) -> stripe.Price:
    return stripe.Price.create(
        currency=price_data['valuta'],
        unit_amount=price_data['price'] * 100,
        nickname=price_data['price_string'],  # f'price for staying {price_data["duration"]} at {price_data["garage_id"]}.'
        product_data={
            'name': f'{price_data["duration"]} at {Garage.objects.get(garage_id=price_data["garage_id"]).name}'
        }
    )
