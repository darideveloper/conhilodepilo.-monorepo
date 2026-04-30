import stripe
from django.conf import settings
from decimal import Decimal

# Set the stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

def get_currency_multiplier(currency: str) -> int:
    """
    Returns the multiplier to convert a decimal amount to the smallest currency unit.
    For most currencies (like EUR, USD) this is 100.
    Zero-decimal currencies like JPY would be 1.
    For simplicity, we default to 100 here, but it can be expanded if needed.
    """
    zero_decimal_currencies = ['bif', 'clp', 'djf', 'gnf', 'jpy', 'kmf', 'krw', 'mga', 'pyg', 'rwf', 'ugx', 'vnd', 'vuv', 'xaf', 'xof', 'xpf']
    if currency.lower() in zero_decimal_currencies:
        return 1
    return 100

def create_checkout_session(booking, total_amount: Decimal, currency: str) -> stripe.checkout.Session:
    """
    Creates a Stripe Checkout session for a given booking.
    Converts the total_amount to the smallest currency unit.
    """
    multiplier = get_currency_multiplier(currency)
    amount_in_cents = int(total_amount * multiplier)

    # Prepare landing site URL
    # Assuming settings.SITE_URL is the base URL without trailing slash
    site_url = settings.SITE_URL.rstrip('/') if settings.SITE_URL else "http://localhost:3000"

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': currency.lower(),
                'product_data': {
                    'name': 'Reserva - Con Hilo Depilo',
                    'description': f'Reserva para {booking.client_name}',
                },
                'unit_amount': amount_in_cents,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"{site_url}/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{site_url}/cancel",
        metadata={
            'booking_id': str(booking.id),
        }
    )
    
    return session
