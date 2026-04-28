from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
from datetime import datetime, time
from .models import CompanyProfile, CompanyWeekdaySlot, EventType, Event, Booking
from .serializers import CompanyProfileSerializer, BusinessHoursSerializer, EventTypeSerializer
from utils.availability import get_available_dates, get_available_slots

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

        booking = Booking.objects.create(
            start_time=start_dt,
            end_time=end_dt,
            client_name=client_name,
            client_email=client_email,
            client_phone=client_phone,
            special_requests=special_requests,
            status="PENDING"
        )
        booking.services.set(services)
        
        return Response({
            "message": "Booking created successfully",
            "booking_id": booking.id,
            "client_name": booking.client_name,
            "client_email": booking.client_email,
            "start_time": booking.start_time.isoformat()
        }, status=201)

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
