from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import time
from .models import CompanyProfile, CompanyWeekdaySlot, EventType, Event, CompanyAvailability, EventDateOverride

class ConfigAPITest(APITestCase):
    def setUp(self):
        self.profile = CompanyProfile.get_solo()
        self.profile.name = "Test Company"
        self.profile.brand_color = "#ee5837"
        self.profile.event_type_label = "Special Category"
        self.profile.save()
        self.url = reverse('api-config')

    def test_get_config_success(self):
        """
        Verify that GET /api/config/ returns 200 and the correct JSON structure.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(data['company_name'], "Test Company")
        self.assertEqual(data['brand_color'], "#ee5837")
        self.assertEqual(data['event_type_label'], "Special Category")
        self.assertIn('timezone', data)
        self.assertIn('currency', data)
        self.assertIn('logo', data)

    def test_public_access(self):
        """
        Verify that the endpoint is accessible without authentication.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BusinessHoursAPITest(APITestCase):
    def setUp(self):
        self.profile = CompanyProfile.get_solo()
        self.url = reverse('api-business-hours')
        
        # Create some test slots
        CompanyWeekdaySlot.objects.create(
            company=self.profile,
            weekday=0, # Monday
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        CompanyWeekdaySlot.objects.create(
            company=self.profile,
            weekday=1, # Tuesday
            start_time=time(10, 0),
            end_time=time(14, 0)
        )

    def test_get_business_hours_success(self):
        """
        Verify that GET /api/business-hours/ returns 200 and the correct JSON structure.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(len(data), 2)
        
        # Verify ordering and content
        self.assertEqual(data[0]['weekday'], 0)
        self.assertEqual(data[0]['start_time'], "09:00:00")
        self.assertEqual(data[0]['end_time'], "17:00:00")

        self.assertEqual(data[1]['weekday'], 1)
        self.assertEqual(data[1]['start_time'], "10:00:00")
        self.assertEqual(data[1]['end_time'], "14:00:00")

    def test_public_access(self):
        """
        Verify that the business hours endpoint is accessible without authentication.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from datetime import time, date, timedelta
from .models import CompanyProfile, CompanyWeekdaySlot, EventType, Event, CompanyAvailability, EventDateOverride

class AvailabilityAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('api-availability-days')
        self.category = EventType.objects.create(name="Tours")
        self.service = Event.objects.create(
            event_type=self.category,
            name="Tour",
            price="100.00",
            duration_minutes=60
        )

    def test_availability_missing_params(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_availability_fallback_to_company(self):
        # Create company availability range
        profile = CompanyProfile.get_solo()
        CompanyAvailability.objects.create(company=profile, start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
        # Need at least one slot
        CompanyWeekdaySlot.objects.create(
            company=profile,
            weekday=date.today().weekday(),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        # Service has no range -> should fallback to company
        response = self.client.get(self.url, {'service_ids': str(self.service.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.json()) > 0)

    def test_availability_override_precedence(self):
        # Set service override to unavailable
        EventDateOverride.objects.create(event=self.service, date=date.today(), is_available=False)
        response = self.client.get(self.url, {'service_ids': str(self.service.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Today should NOT be in the available dates
        self.assertNotIn(date.today().strftime('%Y-%m-%d'), response.json())

class BookingAPITest(APITestCase):
    def setUp(self):
        self.url = reverse('api-bookings')
        self.profile = CompanyProfile.get_solo()
        self.category = EventType.objects.create(name="Tours")
        self.service = Event.objects.create(
            event_type=self.category,
            name="Tour",
            price="100.00",
            duration_minutes=60
        )
        # Set up availability for tomorrow
        self.tomorrow = date.today() + timedelta(days=1)
        CompanyAvailability.objects.create(
            company=self.profile, 
            start_date=self.tomorrow, 
            end_date=self.tomorrow + timedelta(days=1)
        )
        CompanyWeekdaySlot.objects.create(
            company=self.profile,
            weekday=self.tomorrow.weekday(),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )

    def test_create_booking_success(self):
        payload = {
            "service_ids": [self.service.id],
            "date": self.tomorrow.strftime('%Y-%m-%d'),
            "startTime": "10:00",
            "clientName": "John Doe",
            "clientEmail": "john@example.com",
            "clientPhone": "123456789",
            "specialRequests": "Looking forward to it!"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['client_name'], "John Doe")
        
        # Verify booking in DB
        from .models import Booking
        self.assertTrue(Booking.objects.filter(client_email="john@example.com").exists())

    def test_create_booking_unavailable_slot(self):
        payload = {
            "service_ids": [self.service.id],
            "date": self.tomorrow.strftime('%Y-%m-%d'),
            "startTime": "09:00", # Outside business hours
            "clientName": "John Doe",
            "clientEmail": "john@example.com"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no longer available", response.json()['error'])

    def test_create_booking_missing_fields(self):
        payload = {
            "service_ids": [self.service.id],
            "date": self.tomorrow.strftime('%Y-%m-%d'),
            # Missing startTime, clientName, clientEmail
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Missing required fields", response.json()['error'])
