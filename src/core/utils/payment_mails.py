import stripe
from django.core.mail import send_mail
from django.template.loader import render_to_string

from src.core.settings import EMAIL_HOST_USER
from src.users.models import User


class PaymentResult:
    Succeeded = 0
    InvoiceFailed = 1
    CheckoutFailed = 2

def send_payment_mail(result: PaymentResult, user_id: str, invoice_url: str = None):
    user = User.objects.get(pk=user_id)

    if result == PaymentResult.Succeeded:
        msg_plain = render_to_string("payment_succeeded_template.txt", {})
        msg_html = render_to_string("payment_succeeded_template.html", {})
    elif result == PaymentResult.CheckoutFailed:
        msg_plain = render_to_string("checkout_failed_template.txt", {})
        msg_html = render_to_string("checkout_failed_template.html", {})
    elif result == PaymentResult.InvoiceFailed:
        msg_plain = render_to_string(
            "invoice_failed_template.txt", {"checkout_url": invoice_url if invoice_url else ''}
        )
        msg_html = render_to_string(
            "invoice_failed_template.html", {"checkout_url": invoice_url if invoice_url else ''}
        )
    else:
        raise NotImplementedError("This payment result is not implemented in 'send_payment_mail'")

    send_mail(
        f"Parking boys payment {'succeeded' if result == PaymentResult.Succeeded else 'failed'}",
        msg_plain,
        EMAIL_HOST_USER,
        [user.email],
        html_message=msg_html,
    )
