import json
from django.test import TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import date, time, timedelta
from rest_framework.test import APIClient
from .models import CompanyProfile, EventType, Event, Booking, CompanyAvailability, CompanyWeekdaySlot
from googleapiclient.errors import HttpError


@override_settings(
    GOOGLE_SERVICE_ACCOUNT_JSON='{"project_id": "test"}',
    GOOGLE_CALENDAR_ID="test-calendar",
    HOST_DOMAIN="test.com"
)
class GoogleCalendarSyncTest(TransactionTestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile = CompanyProfile.get_solo()
        self.category = EventType.objects.create(name="Tours")
        self.service = Event.objects.create(
            event_type=self.category,
            name="Tour",
            price="100.00",
            duration_minutes=60
        )
        self.tomorrow = date.today() + timedelta(days=1)
        CompanyAvailability.objects.create(
            company=self.profile,
            start_date=self.tomorrow,
            end_date=self.tomorrow + timedelta(days=7)
        )
        CompanyWeekdaySlot.objects.create(
            company=self.profile,
            weekday=self.tomorrow.weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        self.url = reverse('api-bookings')

    @patch('utils.google_calendar.get_google_calendar_service')
    def test_confirmed_booking_creation_triggers_insert(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        mock_service.events().list().execute.return_value = {"items": []}
        mock_service.events().insert().execute.return_value = {"id": "new-event-id"}

        payload = {
            "service_ids": [self.service.id],
            "date": self.tomorrow.strftime('%Y-%m-%d'),
            "startTime": "10:00",
            "clientName": "Test Client",
            "clientEmail": "test@example.com",
            "clientPhone": "123456789"
        }
        
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        
        # In TransactionTestCase, on_commit is called
        self.assertTrue(mock_service.events().insert.called)
        # We check the call on the mock returned by events()
        insert_call = mock_service.events().insert.call_args
        self.assertEqual(insert_call.kwargs['body']['summary'], "Test Client — Tour")
        self.assertEqual(insert_call.kwargs['sendUpdates'], "none")
        self.assertEqual(insert_call.kwargs['body']['extendedProperties']['private']['booking_id'], str(response.data['booking_id']))

    @patch('utils.google_calendar.get_google_calendar_service')
    def test_pending_booking_no_sync(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        self.category.payment_model = "PRE-PAID"
        self.category.save()

        payload = {
            "service_ids": [self.service.id],
            "date": self.tomorrow.strftime('%Y-%m-%d'),
            "startTime": "10:00",
            "clientName": "Test Client",
            "clientEmail": "test@example.com",
        }
        
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertFalse(mock_service.events().insert.called)

    @patch('utils.google_calendar.get_google_calendar_service')
    def test_status_cancelled_patches_with_prefix(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.events().patch().execute.return_value = {"id": "existing-id"}

        booking = Booking.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            client_name="Cancel Me",
            client_email="cancel@example.com",
            google_event_id="existing-id",
            status="CONFIRMED"
        )
        booking.services.add(self.service)
        
        # Reset mock to clear calls from initial m2m sync
        mock_service.events().patch.reset_mock()
        
        booking.status = "CANCELLED"
        booking.save()
        
        self.assertTrue(mock_service.events().patch.called)
        patch_call = mock_service.events().patch.call_args
        self.assertTrue(patch_call.kwargs['body']['summary'].startswith("[CANCELLED]"))

    @patch('utils.google_calendar.get_google_calendar_service')
    def test_lookup_before_insert_recovery(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        # Simulate finding an orphan event
        mock_service.events().list().execute.return_value = {
            "items": [{"id": "found-id"}]
        }
        mock_service.events().patch().execute.return_value = {"id": "found-id"}

        booking = Booking.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            client_name="Ghost",
            client_email="ghost@example.com",
            status="CONFIRMED"
        )
        booking.services.add(self.service)
        
        self.assertTrue(mock_service.events().list.called)
        self.assertTrue(mock_service.events().patch.called)
        self.assertFalse(mock_service.events().insert.called)
        
        booking.refresh_from_db()
        self.assertEqual(booking.google_event_id, "found-id")

    @override_settings(TIME_ZONE="Europe/Paris")
    def test_timezone_consistency(self):
        from utils.google_calendar import booking_to_event_body
        booking = Booking.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            client_name="TZ Test",
            client_email="tz@example.com"
        )
        body = booking_to_event_body(booking)
        self.assertEqual(body['start']['timeZone'], "Europe/Paris")

    @patch('utils.google_calendar.get_google_calendar_service')
    def test_delete_404_success(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        resp = MagicMock()
        resp.status = 404
        resp.reason = "Not Found"
        mock_service.events().delete().execute.side_effect = HttpError(resp, b'{}')

        booking = Booking.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            client_name="Delete 404",
            client_email="404@example.com",
            google_event_id="missing-id"
        )
        
        booking.delete()
        self.assertTrue(mock_service.events().delete.called)

    @patch('utils.google_calendar.get_google_calendar_service')
    def test_reconcile_command_retries_failure(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_service.events().list().execute.return_value = {"items": []}
        mock_service.events().insert().execute.return_value = {"id": "recovered-id"}

        booking = Booking.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            client_name="Failure Retry",
            client_email="fail@example.com",
            google_sync_status="FAILURE"
        )
        booking.services.add(self.service)
        
        from django.core.management import call_command
        call_command('reconcile_google_calendar')
        
        booking.refresh_from_db()
        self.assertEqual(booking.google_sync_status, "SUCCESS")
        self.assertEqual(booking.google_event_id, "recovered-id")
