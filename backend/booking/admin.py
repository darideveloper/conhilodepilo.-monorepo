from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from unfold.admin import ModelAdmin, TabularInline
from unfold.widgets import UnfoldAdminColorInputWidget
from project.admin import ModelAdminUnfoldBase
from solo.admin import SingletonModelAdmin
from .models import (
    CompanyProfile,
    EventTypeGroup,
    EventType,
    Event,
    CompanyAvailability,
    CompanyWeekdaySlot,
    CompanyDateOverride,
    EventAvailability,
    AvailabilitySlot,
    EventDateOverride,
    Booking,
)

class BaseTabularInline(TabularInline):
    tab = True
    extra = 0

class AvailabilitySlotInline(BaseTabularInline):
    fields = ("weekday", "start_time", "end_time")

    def get_extra(self, request, obj=None, **kwargs):
        related_name = getattr(self, "related_name_attr", "slots")
        if obj and getattr(obj, related_name).exists():
            return 0
        return 7

    def get_formset(self, request, obj=None, **kwargs):
        FormSet = super().get_formset(request, obj, **kwargs)
        related_name = getattr(self, "related_name_attr", "slots")
        
        class InitialFormSet(FormSet):
            def __init__(self, *args, **kwargs):
                if not kwargs.get("initial") and (obj is None or not getattr(obj, related_name).exists()):
                    kwargs["initial"] = [{"weekday": i} for i in range(7)]
                super().__init__(*args, **kwargs)
        return InitialFormSet

class CompanyWeekdaySlotInline(AvailabilitySlotInline):
    model = CompanyWeekdaySlot
    related_name_attr = "weekday_slots"

class CompanyAvailabilityInline(BaseTabularInline):
    model = CompanyAvailability

class CompanyDateOverrideInline(BaseTabularInline):
    model = CompanyDateOverride

class EventAvailabilitySlotInline(BaseTabularInline):
    model = AvailabilitySlot
    fields = ("weekday", "start_time", "end_time")

class EventAvailabilityInline(BaseTabularInline):
    model = EventAvailability

class EventDateOverrideInline(BaseTabularInline):
    model = EventDateOverride

class BookingInline(BaseTabularInline):
    model = Booking.services.through
    verbose_name = _("Booking")
    verbose_name_plural = _("Bookings")
    fields = ("client_name", "start_time", "status", "manage_booking")
    readonly_fields = fields
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def client_name(self, obj):
        return obj.booking.client_name
    client_name.short_description = _("Client")

    def start_time(self, obj):
        return obj.booking.start_time
    start_time.short_description = _("Date/Time")

    def status(self, obj):
        return obj.booking.get_status_display()
    status.short_description = _("Status")

    def manage_booking(self, obj):
        if not obj.pk:
            return ""
        url = reverse("admin:booking_booking_change", args=[obj.booking.pk])
        return format_html(
            '<a class="bg-primary-600 font-medium px-4 py-1 rounded-md text-white text-xs" href="{}">{}</a>',
            url,
            _("Manage")
        )
    manage_booking.short_description = _("Actions")

class EventInline(BaseTabularInline):
    model = Event
    fields = ("name", "price", "duration_minutes")
    readonly_fields = ("name", "price", "duration_minutes")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(CompanyProfile)
class CompanyProfileAdmin(SingletonModelAdmin, ModelAdminUnfoldBase):
    inlines = [
        CompanyAvailabilityInline,
        CompanyWeekdaySlotInline,
        CompanyDateOverrideInline,
    ]

    fieldsets = (
        (_("General"), {
            "fields": (
                "name",
                "brand_color",
                "logo",
                "currency",
            )
        }),
        (_("Contact Information"), {
            "fields": (
                "contact_email",
                "contact_phone",
            )
        }),
        (_("UI Labels"), {
            "fields": (
                "event_type_label",
                "event_label",
                "availability_free_label",
                "availability_regular_label",
                "availability_no_free_label",
                "extras_label",
            )
        }),
    )

    tabs = [
        (_("General"), ["fieldsets"]),
        (_("UI Labels"), ["fieldsets"]),
        (_("Global Availability"), ["availabilities"]),
        (_("Business Hours"), ["weekday_slots"]),
        (_("Holidays"), ["overrides"]),
    ]

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "brand_color":
            kwargs["widget"] = UnfoldAdminColorInputWidget
        return super().formfield_for_dbfield(db_field, **kwargs)

@admin.register(EventTypeGroup)
class EventTypeGroupAdmin(ModelAdminUnfoldBase):
    list_display = ("name",)

@admin.register(EventType)
class EventTypeAdmin(ModelAdminUnfoldBase):
    list_display = ("name", "group", "payment_model", "allow_overlap")
    list_filter = ("group", "payment_model")
    inlines = [EventInline]

    fieldsets = (
        (_("General"), {
            "fields": (
                "group",
                "name",
                "description",
                "payment_model",
                "allow_overlap",
                "image",
            )
        }),
    )

    tabs = [
        (_("General"), ["fieldsets"]),
        (_("Servicios"), ["events"]),
    ]

@admin.register(Event)
class EventAdmin(ModelAdminUnfoldBase):
    list_display = ("name", "event_type", "price", "duration_minutes")
    list_filter = ("event_type",)
    inlines = [
        EventAvailabilityInline,
        EventAvailabilitySlotInline,
        EventDateOverrideInline,
        BookingInline,
    ]

    fieldsets = (
        (_("General"), {
            "fields": (
                "event_type",
                "name",
                "description",
                "price",
                "duration_minutes",
                "image",
            )
        }),
    )

    tabs = [
        (_("General"), ["fieldsets"]),
        (_("Service Week Slots"), ["slots"]),
        (_("Service Availability"), ["availabilities"]),
        (_("Service Date Overrides"), ["overrides"]),
        (_("Booking"), ["bookings"]),
    ]

@admin.register(CompanyAvailability)
class CompanyAvailabilityAdmin(ModelAdminUnfoldBase):
    list_display = ("start_date", "end_date")

@admin.register(CompanyWeekdaySlot)
class CompanyWeekdaySlotAdmin(ModelAdminUnfoldBase):
    list_display = ("weekday", "start_time", "end_time")
    list_filter = ("weekday",)

@admin.register(CompanyDateOverride)
class CompanyDateOverrideAdmin(ModelAdminUnfoldBase):
    list_display = ("date", "is_available", "start_time", "end_time")

@admin.register(EventAvailability)
class EventAvailabilityAdmin(ModelAdminUnfoldBase):
    list_display = ("event", "start_date", "end_date")
    list_filter = ("event",)

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(ModelAdminUnfoldBase):
    list_display = ("event", "weekday", "start_time", "end_time")
    list_filter = ("event", "weekday")

@admin.register(EventDateOverride)
class EventDateOverrideAdmin(ModelAdminUnfoldBase):
    list_display = ("event", "date", "is_available", "start_time", "end_time")
    list_filter = ("event",)

@admin.register(Booking)
class BookingAdmin(ModelAdminUnfoldBase):
    list_display = ("client_name", "start_time", "end_time", "status")
    list_filter = ("status", "start_time")
    search_fields = ("client_name", "client_email")
    filter_horizontal = ("services",)
    readonly_fields = ("end_time",)
    
    fieldsets = (
        (_("Client Information"), {
            "fields": ("client_name", "client_email", "client_phone")
        }),
        (_("Scheduling"), {
            "fields": ("start_time", "end_time", "status")
        }),
        (_("Services"), {
            "fields": ("services",)
        }),
        (_("Integrations"), {
            "fields": ("google_event_id", "stripe_payment_id"),
            "classes": ("collapse",)
        }),
    )
