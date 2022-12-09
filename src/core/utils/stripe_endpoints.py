from os import getenv

import stripe

from src.api.models import LicencePlate
from src.api.models.garages.garage import Garage
from src.users.models import User

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


def create_stripe_customer(user: User, card_data:dict) -> str:

    customer: stripe.Customer = stripe.Customer.create(
        email=user.email, # Use your email address for testing purposes
        description="",
    )
    # Store the customer ID in your database for future purchases
    # CUSTOMERS.append({"stripe_id": customer.id, "email": email})
    # Read the Customer ID from your database
    customer_id = customer.id

    payment_method: stripe.PaymentMethod = stripe.PaymentMethod.create(
        type='card',
        card=card_data,
    )

    payment_method.attach(customer=customer_id)

    return customer_id

def remove_stripe_customer(user: User):

    if user.stripe_identifier is not None:
        stripe.Customer.delete(user.stripe_identifier)

    # TODO: Check if payment method should be removed too, or if this is done automatically


def send_invoice(user: User, licence_plate: LicencePlate) -> None:
    # Look up a customer in your database

    if user.is_connected_to_stripe:
        stripe_identifier = user.stripe_identifier
        # Get items to pay for licence plate
        items, _ = licence_plate.get_prices_to_pay(licence_plate)

        # Create an Invoice
        invoice = stripe.Invoice.create(
            customer=stripe_identifier,
            collection_method='send_invoice',
            days_until_due=30,
        )

        for item in items:
            for _ in range(item['quantity']):
                # Create an Invoice Item with the Price and Customer you want to charge
                stripe.InvoiceItem.create(
                    customer=stripe_identifier,
                    price=item['price'].stripe_identifier,
                    invoice=invoice.id,
                )

        # Send the Invoice
        stripe.Invoice.send_invoice(invoice.id)