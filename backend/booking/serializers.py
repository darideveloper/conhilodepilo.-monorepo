from rest_framework import serializers
from .models import CompanyProfile, CompanyWeekdaySlot, Event, EventType

class CompanyProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='name')

    class Meta:
        model = CompanyProfile
        fields = [
            'company_name',
            'brand_color',
            'logo',
            'currency',
            'contact_email',
            'contact_phone',
            'event_type_label',
            'event_label',
            'availability_free_label',
            'availability_regular_label',
            'availability_no_free_label',
            'extras_label',
        ]

class BusinessHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyWeekdaySlot
        fields = ['weekday', 'start_time', 'end_time']

class EventSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='name')
    duration = serializers.IntegerField(source='duration_minutes')

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'price', 'duration', 'image']

class EventTypeSerializer(serializers.ModelSerializer):
    services = EventSerializer(source='events', many=True, read_only=True)
    group_id = serializers.ReadOnlyField(source='group.id')

    class Meta:
        model = EventType
        fields = ['id', 'name', 'description', 'image', 'services', 'group_id']
