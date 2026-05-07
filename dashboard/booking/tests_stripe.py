from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date, time, timedelta
from django.utils import timezone
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APIClient
from io import StringIO
from datetime import timedelta
from django.core.management import call_command
import stripe
from .models import CompanyProfile, EventType, Event, Booking

@override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_WEBHOOK_SECRET="whsec_123", LANDING_URL="http://test-landing.com")
class CleanupAbandonedBookingsTest(TestCase):
    def setUp(self):
        self.now = timezone.now()
        
        # Recent pending booking (should be preserved)
        self.recent_pending = Booking.objects.create(
            start_time=self.now,
            client_name="Recent Pending",
            client_email="recent@example.com",
            status="PENDING"
        )
        
        # Old pending booking (should be deleted)
        self.old_pending = Booking.objects.create(
            start_time=self.now,
            client_name="Old Pending",
            client_email="old@example.com",
            status="PENDING"
        )
        # Manually backdate created_at to bypass auto_now_add
        Booking.objects.filter(id=self.old_pending.id).update(
            created_at=self.now - timedelta(hours=25)
        )
        
        # Old confirmed booking (should be preserved)
        self.old_confirmed = Booking.objects.create(
            start_time=self.now,
            client_name="Old Confirmed",
            client_email="old-conf@example.com",
            status="CONFIRMED"
        )
        Booking.objects.filter(id=self.old_confirmed.id).update(
            created_at=self.now - timedelta(hours=25)
        )

    def test_cleanup_deletes_old_pending_only(self):
        """
        Verify that only PENDING bookings older than TTL are deleted.
        """
        out = StringIO()
        call_command('cleanup_abandoned_bookings', stdout=out)
        
        # old_pending should be gone
        self.assertFalse(Booking.objects.filter(id=self.old_pending.id).exists())
        
        # recent_pending should remain
        self.assertTrue(Booking.objects.filter(id=self.recent_pending.id).exists())
        
        # old_confirmed should remain
        self.assertTrue(Booking.objects.filter(id=self.old_confirmed.id).exists())
        
        self.assertIn("Successfully deleted 1 abandoned booking(s)", out.getvalue())

    def test_cleanup_dry_run(self):
        """
        Verify that --dry-run does not delete any records.
        """
        out = StringIO()
        call_command('cleanup_abandoned_bookings', '--dry-run', stdout=out)
        
        # All bookings should remain
        self.assertTrue(Booking.objects.filter(id=self.old_pending.id).exists())
        self.assertTrue(Booking.objects.filter(id=self.recent_pending.id).exists())
        self.assertTrue(Booking.objects.filter(id=self.old_confirmed.id).exists())
        
        self.assertIn("[DRY RUN] Would delete 1 abandoned booking(s)", out.getvalue())

@override_settings(STRIPE_SECRET_KEY="sk_test_123", STRIPE_WEBHOOK_SECRET="whsec_123", LANDING_URL="http://test-landing.com")
class StripeIntegrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile = CompanyProfile.get_solo()
        self.profile.currency = "EUR"
        self.profile.save()

        self.category = EventType.objects.create(name="Tours", payment_model="PRE-PAID")
        self.service = Event.objects.create(
            event_type=self.category,
            name="Prepaid Tour",
            price=Decimal("150.50"),
            duration_minutes=60
        )
        
        self.post_paid_category = EventType.objects.create(name="Consultations", payment_model="POST-PAID")
        self.post_paid_service = Event.objects.create(
            event_type=self.post_paid_category,
            name="Free Consult",
            price=Decimal("0.00"),
            duration_minutes=30
        )

        self.tomorrow = date.today() + timedelta(days=1)
        # Mock availability for tomorrow
        from .models import CompanyAvailability, CompanyWeekdaySlot
        CompanyAvailability.objects.create(company=self.profile, start_date=self.tomorrow, end_date=self.tomorrow)
        CompanyWeekdaySlot.objects.create(
            company=self.profile, 
            weekday=self.tomorrow.weekday(), 
            start_time=time(9, 0), 
            end_time=time(17, 0)
        )

    @patch('utils.stripe_utils.stripe.checkout.Session.create')
    def test_create_booking_with_stripe_redirect(self, mock_session_create):
        """
        Verify that a booking with PRE-PAID services triggers Stripe session creation
        and returns a checkout URL.
        """
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"
        mock_session_create.return_value = mock_session

        url = reverse('api-bookings')
        payload = {
            "service_ids": [self.service.id],
            "date": self.tomorrow.strftime('%Y-%m-%d'),
            "startTime": "10:00",
            "clientName": "Stripe User",
            "clientEmail": "stripe@example.com"
        }

        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['payment_required'])
        self.assertEqual(data['checkout_url'], "https://checkout.stripe.com/pay/cs_test_123")
        
        # Verify multiplier (150.50 * 100 = 15050)
        mock_session_create.assert_called_once()
        args, kwargs = mock_session_create.call_args
        self.assertEqual(kwargs['line_items'][0]['price_data']['unit_amount'], 15050)
        self.assertEqual(kwargs['success_url'], "http://test-landing.com/success?session_id={CHECKOUT_SESSION_ID}")

    @patch('utils.stripe_utils.stripe.checkout.Session.create')
    def test_create_checkout_session_product_name(self, mock_session_create):
        """
        Verify that create_checkout_session uses the CompanyProfile name.
        """
        from utils.stripe_utils import create_checkout_session
        from django.core.cache import cache
        
        self.profile.name = "My Studio"
        self.profile.save()
        cache.clear()

        booking = Booking.objects.create(
            start_time=timezone.now(),
            client_name="Test Client",
            client_email="test@example.com",
            status="PENDING"
        )

        create_checkout_session(booking, Decimal("50.00"), "EUR")
        
        mock_session_create.assert_called_once()
        kwargs = mock_session_create.call_args[1]
        self.assertEqual(kwargs['line_items'][0]['price_data']['product_data']['name'], "My Studio")

    def test_create_booking_post_paid_skips_stripe(self):
        """
        Verify that a booking with only POST-PAID services is confirmed immediately.
        """
        url = reverse('api-bookings')
        payload = {
            "service_ids": [self.post_paid_service.id],
            "date": self.tomorrow.strftime('%Y-%m-%d'),
            "startTime": "11:00",
            "clientName": "Regular User",
            "clientEmail": "regular@example.com"
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertFalse(data['payment_required'])
        self.assertNotIn('checkout_url', data)
        
        # Verify status in DB
        booking = Booking.objects.get(client_email="regular@example.com")
        self.assertEqual(booking.status, "CONFIRMED")

    @patch('stripe.Webhook.construct_event')
    def test_webhook_successful_payment(self, mock_construct_event):
        """
        Verify that a successful payment webhook updates the booking status to PAID.
        """
        booking = Booking.objects.create(
            start_time=timezone.now(),
            client_name="Webhook Test",
            client_email="webhook@example.com",
            status="PENDING"
        )
        
        # Mock Stripe event
        mock_construct_event.return_value = {
            'id': 'evt_test_123',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'metadata': {'booking_id': str(booking.id)},
                    'payment_intent': 'pi_test_123'
                }
            }
        }

        url = reverse('stripe-webhook')
        response = self.client.post(url, data={}, HTTP_STRIPE_SIGNATURE="mock_sig")
        
        self.assertEqual(response.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, "PAID")
        self.assertEqual(booking.stripe_payment_id, "pi_test_123")

    @patch('stripe.Webhook.construct_event')
    def test_webhook_invalid_signature(self, mock_construct_event):
        """
        Verify that webhooks with invalid signatures are rejected.
        """
        mock_construct_event.side_effect = stripe.SignatureVerificationError("Invalid", "sig")

        url = reverse('stripe-webhook')
        response = self.client.post(url, data={}, HTTP_STRIPE_SIGNATURE="invalid_sig")

        self.assertEqual(response.status_code, 400)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_csrf_exempt(self, mock_construct_event):
        """
        Verify that the webhook view is exempt from CSRF and accepts requests 
        even if a session cookie is present but no CSRF token is provided.
        """
        mock_construct_event.return_value = {
            'id': 'evt_test_csrf',
            'type': 'checkout.session.completed',
            'data': {'object': {}}
        }

        url = reverse('stripe-webhook')

        # Test without cookie (should pass signature check and return 200)
        response_no_cookie = self.client.post(url, data={}, HTTP_STRIPE_SIGNATURE="mock_sig")
        self.assertEqual(response_no_cookie.status_code, 200)

        # Test with a mocked session cookie to trigger DRF SessionAuthentication CSRF check 
        # (if it wasn't exempted). It should still pass.
        self.client.cookies['sessionid'] = 'mocked_session_id'
        response_with_cookie = self.client.post(url, data={}, HTTP_STRIPE_SIGNATURE="mock_sig")
        self.assertEqual(response_with_cookie.status_code, 200)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_idempotency(self, mock_construct_event):
        """
        Verify that the webhook handler is idempotent.
        Posting the same event twice should update the booking exactly once.
        The second delivery should return 200 without raising an error.
        """
        booking = Booking.objects.create(
            start_time=timezone.now(),
            client_name="Webhook Idempotent",
            client_email="idempotent@example.com",
            status="PENDING"
        )
        
        mock_construct_event.return_value = {
            'id': 'evt_test_idempotent',
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'metadata': {'booking_id': str(booking.id)},
                    'payment_intent': 'pi_test_idem'
                }
            }
        }

        url = reverse('stripe-webhook')
        
        # First delivery
        response1 = self.client.post(url, data={}, HTTP_STRIPE_SIGNATURE="mock_sig")
        self.assertEqual(response1.status_code, 200)
        
        booking.refresh_from_db()
        self.assertEqual(booking.status, "PAID")
        
        # Change status back to PENDING manually to verify it doesn't get updated again
        booking.status = "PENDING"
        booking.save()
        
        # Second delivery
        response2 = self.client.post(url, data={}, HTTP_STRIPE_SIGNATURE="mock_sig")
        self.assertEqual(response2.status_code, 200)
        
        booking.refresh_from_db()
        # Should still be PENDING because the webhook short-circuited due to idempotency
        self.assertEqual(booking.status, "PENDING")
