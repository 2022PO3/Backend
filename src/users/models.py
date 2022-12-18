import io
import os
import cv2
import stripe
from qrcode import make, QRCode


from secrets import token_hex
from knox.models import AuthToken

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from src.api.models.licence_plate import LicencePlate

from src.users.managers import UserManager
from src.api.models import ProvincesEnum
from src.core.models import TimeStampMixin
from src.core.exceptions import DeletionException
from src.core.exceptions import BackendException


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
publishableKey = os.getenv("STRIPE_PUBLISHABLE_KEY")


class User(AbstractBaseUser, TimeStampMixin, PermissionsMixin):
    class Roles(models.IntegerChoices):
        GENERATED_USER = 0
        NORMAL_USER = 1
        GARAGE_OWNER = 2
        ADMIN = 3

    first_name = models.CharField(max_length=192, null=True)
    last_name = models.CharField(max_length=192, null=True)
    email = models.EmailField(unique=True)
    role = models.IntegerField(choices=Roles.choices)
    is_active = models.BooleanField(default=True)
    two_factor = models.BooleanField(default=False)
    two_factor_validated = models.BooleanField(null=True, blank=True)
    fav_garage = models.ForeignKey(
        "api.Garage", on_delete=models.CASCADE, null=True, related_name="fav_garage"
    )
    location = models.CharField(max_length=3, choices=ProvincesEnum.choices, null=True)
    stripe_identifier = models.CharField(max_length=18, null=True)
    strikes = models.IntegerField()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    objects = UserManager()

    def delete(self) -> tuple[int, dict[str, int]]:
        from src.api.models import LicencePlate, Reservation

        if self.is_garage_owner:
            raise DeletionException(
                "You're a garage owner, thus your account cannot be directly deleted. Please contact support if you wish to continue."
            )
        user_lps = LicencePlate.objects.filter(user_id=self.pk)
        for lp in user_lps:
            lp.delete()
        user_reservations = Reservation.objects.filter(user_id=self.pk)
        for reservation in user_reservations:
            reservation.delete()
        user_tokens = AuthToken.objects.filter(user_id=self.pk)
        for token in user_tokens:
            token.delete()
        return super().delete()

    def notify(self, title: str, content: str) -> None:
        """
        Creates a notification for the user.
        """
        from src.api.models import Notification

        Notification.objects.create(
            user=self.pk,
            seen=False,
            title=title,
            content=content,
        )

    def enable_2fa(self) -> None:
        self.two_factor = True
        self.two_factor_validated = False
        self.save()

    def disable_2fa(self) -> None:
        self.two_factor = False
        self.two_factor_validated = None
        self.save()

    def validated_2fa(self) -> None:
        self.two_factor_validated = True
        self.save()

    def increase_strikes(self, reservation) -> None:
        """
        Increases the strike number for the current user with 1.
        If the user gets three strikes, the user will be deactivated.
        Will set a notification to the user to notify him that the strike number has increased.
        """
        self.strikes += 1
        if self.strikes == 3:
            self.is_active = False
        else:
            self.notify(
                "Got extra strike",
                "You did not show up for the reservation in {reservation.garage.name}, where you booked from {reservation.from_date} to {reservation.to_date}. Therefore your strikes have increased to {self.strikes}. When you receive your third strike, your account will be deactivated for one month.",
            )

    def _generate_log_in_url(self, password: str) -> str:
        """
        Generates a url for logging into the Frontend application given a generated user's email and password.
        Returns the URL.
        """
        return f"https://po3backend.ddns.net/app/login?email={self.email}&password={password}"

    def generate_qr_code(self, password: str) -> None:
        """
        Generates a QR-code for logging into the Frontend application given a generated user's email and password.
        The QR-code is saved in the folder qr_codes.
        """
        img = make(self._generate_log_in_url(password))
        img.save(
            os.path.join(
                os.getcwd(), f"src/api/qr_codes/{self.email.split('@')[0]}.png"
            )
        )

    def print_qr_code(self) -> None:
        """
        Prints a QR code to stdout from a generated user.
        """
        if not self.is_generated_user:
            raise BackendException(
                "User is not a generated user, thus no QR code exists."
            )
        else:
            f = io.StringIO()
            _read_qr_code(
                os.path.join(
                    os.getcwd(), f"src/api/qr_codes/{self.email.split('@')[0]}.png"
                )
            ).print_ascii(out=f)
            f.seek(0)
            print(f.read())

    def delete_qr_code(self) -> None:
        """
        Delete the QR code associated with the generated user.
        """
        if not self.is_generated_user:
            raise BackendException(
                "User is not a generated user, thus no QR code exists."
            )
        path = os.path.join(
            os.getcwd(), f"src/api/qr_codes/{self.email.split('@')[0]}.png"
        )
        if os.path.exists(path):
            os.remove(path)

    @property
    def is_admin(self) -> bool:
        return self.role == 3

    @property
    def is_garage_owner(self) -> bool:
        return self.role == 2

    @property
    def is_normal_user(self) -> bool:
        return self.role == 1

    @property
    def is_generated_user(self) -> bool:
        return self.role == 0

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def has_automatic_payment(self) -> bool:
        return self.stripe_identifier is not None

    @staticmethod
    def email_generator() -> str:
        """
        Generates a random email address.
        """
        return f"{token_hex(8)}@generated.com"

    def create_stripe_customer(self, card_data: dict) -> str:
        customer: stripe.Customer = stripe.Customer.create(
            email=self.email,  # Use your email address for testing purposes
            description="",
        )
        # Store the customer ID in your database for future purchases
        # CUSTOMERS.append({"stripe_id": customer.id, "email": email})
        # Read the Customer ID from your database
        customer_id = customer.id

        try:
            payment_method: stripe.PaymentMethod = stripe.PaymentMethod.create(
                type="card",
                card=card_data,
            )
            payment_method.attach(customer=customer_id)
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method.stripe_id},
            )
        except Exception as e:
            customer.delete()
            raise e
        return customer_id

    def remove_stripe_customer(self):
        if self.stripe_identifier is not None:
            stripe.Customer.delete(self.stripe_identifier)

    def send_invoice(self, licence_plate: LicencePlate) -> None:
        # Look up a customer in your database

        if self.has_automatic_payment:
            stripe_identifier = self.stripe_identifier
            # Get items to pay for licence plate
            items, _ = licence_plate.get_prices_to_pay()

            # Create an Invoice
            invoice = stripe.Invoice.create(
                customer=stripe_identifier,
                auto_advance=True,
                collection_method="charge_automatically",
                metadata={
                    "user_id": self.pk,
                    "licence_plate": licence_plate.licence_plate,
                },
            )

            for item in items:
                price: Price = item["price"]  # type: ignore
                # Create an Invoice Item with the Price and Customer you want to charge
                stripe.InvoiceItem.create(
                    customer=stripe_identifier,
                    amount=int(price.price * 100 * item["quantity"]),  # type: ignore
                    description=f'{price.price_string} x{item["quantity"]}',
                    # price=item['price'].stripe_identifier,
                    invoice=invoice.id,
                    currency=price.valuta,
                )

            # Complete invoice, this will send a request to the webhook view which then can use invoice.pay() to charge
            # the user.
            invoice.finalize_invoice()
        else:
            raise BackendException("User is not connected to stripe")


def _read_qr_code(qr_code_path: str) -> QRCode:
    """
    Reads a QR-code from an local image path and returns a QR-code object.
    """
    image = cv2.imread(qr_code_path)
    detector = cv2.QRCodeDetector()
    data, vertices_array, _ = detector.detectAndDecode(image)

    if vertices_array is not None:
        qr_code = QRCode()
        qr_code.add_data(data)
        return qr_code
    else:
        raise BackendException("QR-code could not be read.")
