from os import getenv

import stripe

from src.api.models.garages.garage import Garage

stripe.api_key = getenv('STRIPE_KEY')
publishableKey = 'pk_test_51Lf1SsGRh96C3wQGiqIisWUuj9dpkWtvEaoeZMJdBU7auHaj9cpW1v9KJEtP3atr5Ws3gcLJOeKMmiNJkRvQqbX200sC5tZ7CE'


def get_stripe_price(price_id):
    return stripe.Price.retrieve(price_id)


def update_stripe_price(price_data):
    return stripe.Price.modify(
        price_data['stripe_identifier'],
        currency=price_data['valuta'],
        unit_amount=price_data['price'] * 100,
        nickname=price_data['price_string'],
        product_data={
            'name': f'{price_data["duration"]} at {Garage.objects.get(garage_id=price_data["garage_id"]).name}'
        }
    )


def create_stripe_price(price_data):
    return stripe.Price.create(
        currency=price_data['valuta'],
        unit_amount=price_data['price'] * 100,
        nickname=price_data['price_string'],  # f'price for staying {price_data["duration"]} at {price_data["garage_id"]}.'
        product_data={
            'name': f'{price_data["duration"]} at {Garage.objects.get(garage_id=price_data["garage_id"]).name}'
        }
    )
