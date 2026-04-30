from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
from datetime import datetime, time
import stripe
from .models import CompanyProfile, CompanyWeekdaySlot, EventType, Event, Booking
from .serializers import CompanyProfileSerializer, BusinessHoursSerializer, EventTypeSerializer
from utils.availability import get_available_dates, get_available_slots
from utils.stripe_utils import create_checkout_session

class CreateBookingView(APIView):
    """
    Public endpoint to create a new booking.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        service_ids = request.data.get('service_ids')
        date_str = request.data.get('date')
        start_time_str = request.data.get('startTime')
        client_name = request.data.get('clientName')
        client_email = request.data.get('clientEmail')
        client_phone = request.data.get('clientPhone')
        special_requests = request.data.get('specialRequests', "")

        if not all([service_ids, date_str, start_time_str, client_name, client_email]):
            return Response({"error": "Missing required fields"}, status=400)

        try:
            ids = [int(sid) for sid in service_ids]
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
        except (ValueError, TypeError):
            return Response({"error": "Invalid format for service_ids, date, or startTime"}, status=400)

        # 1. Validate services exist
        services = list(Event.objects.filter(id__in=ids))
        if len(services) != len(ids):
            return Response({"error": "One or more services not found"}, status=400)

        # 2. Check availability
        available_slots = get_available_slots(target_date, ids)
        if start_time_str not in available_slots:
            return Response({"error": "Selected time slot is no longer available"}, status=400)

        # 3. Create Booking
        start_dt = timezone.make_aware(datetime.combine(target_date, start_time))
        total_duration = sum(s.duration_minutes for s in services)
        end_dt = start_dt + timezone.timedelta(minutes=total_duration)

        # Check if any service requires pre-payment
        is_pre_paid = any(s.event_type.payment_model == "PRE-PAID" for s in services)
        status = "PENDING" if is_pre_paid else "CONFIRMED"

        booking = Booking.objects.create(
            start_time=start_dt,
            end_time=end_dt,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            special_requests=special_requests,
            status=status
        )
        booking.services.set(services)
        
        response_data = {
            "message": "Booking created successfully",
            "booking_id": booking.id,
            "client_name": booking.client_name,
            "client_email": booking.client_email,
            "start_time": booking.start_time.isoformat(),
            "payment_required": is_pre_paid
        }

        if is_pre_paid:
            total_amount = sum(s.price for s in services)
            company = CompanyProfile.get_solo()
            try:
                session = create_checkout_session(booking, total_amount, company.currency)
                response_data["checkout_url"] = session.url
            except stripe.StripeError:
                # If we cannot create the Stripe session, delete the booking and return error
                booking.delete()
                return Response({"error": "Payment service is currently unavailable. Please try again later."}, status=503)

        return Response(response_data, status=201)

class CompanyConfigView(APIView):
    """
    Public endpoint to fetch company branding, contact details, and UI labels.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        config = CompanyProfile.get_solo()
        serializer = CompanyProfileSerializer(config, context={'request': request})
        data = serializer.data
        
        # Inject system timezone
        data['timezone'] = settings.TIME_ZONE
        
        return Response(data)

class BusinessHoursView(APIView):
    """
    Public endpoint to fetch company business hours (weekday slots).
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        config = CompanyProfile.get_solo()
        slots = config.weekday_slots.all().order_by('weekday', 'start_time')
        serializer = BusinessHoursSerializer(slots, many=True)
        return Response(serializer.data)

class ServicesListView(APIView):
    """
    Public endpoint to fetch all service categories and their associated services.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        categories = EventType.objects.prefetch_related('events').all()
        serializer = EventTypeSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

class AvailabilityView(APIView):
    """
    Public endpoint to check available days for selected services.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        service_ids = request.query_params.get('service_ids')
        if not service_ids:
            return Response({"error": "service_ids is required"}, status=400)
            
        try:
            ids = [int(sid) for sid in service_ids.split(',')]
        except ValueError:
            return Response({"error": "Invalid service_ids format"}, status=400)
            
        available_dates = get_available_dates(ids)
        return Response(available_dates)

class AvailabilitySlotsView(APIView):
    """
    Public endpoint to check available time slots for selected services on a specific date.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        service_ids = request.query_params.get('service_ids')
        date_str = request.query_params.get('date')
        
        if not service_ids or not date_str:
            return Response({"error": "service_ids and date are required"}, status=400)
            
        try:
            ids = [int(sid) for sid in service_ids.split(',')]
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return Response({"error": "Invalid service_ids or date format (YYYY-MM-DD)"}, status=400)
            
        slots = get_available_slots(target_date, ids)
        return Response(slots)

class StripeWebhookView(APIView):
    """
    Public endpoint to handle Stripe webhooks.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        if not endpoint_secret:
            return Response({"error": "Webhook secret not configured"}, status=400)

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return Response(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return Response(status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            booking_id = session.get('metadata', {}).get('booking_id')
            if booking_id:
                try:
                    booking = Booking.objects.get(id=booking_id)
                    if booking.status == 'PENDING':
                        booking.status = 'PAID'
                        booking.stripe_payment_id = session.get('payment_intent') or session.get('id')
                        booking.save(update_fields=['status', 'stripe_payment_id'])
                        
                        # Note: Google Calendar sync will be triggered by a signal
                except Booking.DoesNotExist:
                    pass

        return Response(status=200)
