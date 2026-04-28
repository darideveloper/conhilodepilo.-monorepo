from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

# --- Abstract Bases ---

class BaseAvailabilityRange(models.Model):
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.start_date} - {self.end_date}"

    def clean(self):
        if self.start_date > self.end_date:
            raise ValidationError(_("Start date cannot be after end date."))

class BaseAvailabilitySlot(models.Model):
    WEEKDAYS = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]
    weekday = models.IntegerField(_("Weekday"), choices=WEEKDAYS)
    start_time = models.TimeField(_("Start time"))
    end_time = models.TimeField(_("End time"))

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.get_weekday_display()}: {self.start_time} - {self.end_time}"

    def clean(self):
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(_("Start time must be before end time."))

class BaseDateOverride(models.Model):
    date = models.DateField(_("Date"))
    is_available = models.BooleanField(_("Is available"), default=False)
    start_time = models.TimeField(_("Start time"), null=True, blank=True)
    end_time = models.TimeField(_("End time"), null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        status = _("Available") if self.is_available else _("Unavailable")
        if self.is_available:
            return f"{self.date} ({status}: {self.start_time} - {self.end_time})"
        return f"{self.date} ({status})"

    def clean(self):
        if self.is_available:
            if not self.start_time or not self.end_time:
                raise ValidationError(_("Start and end times are required if available."))
            if self.start_time >= self.end_time:
                raise ValidationError(_("Start time must be before end time."))
        elif self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(_("Start time must be before end time."))

# --- Company Profile ---

class CompanyProfile(SingletonModel):
    name = models.CharField(_("Name"), max_length=100, default="Con Hilo Depilo")
    brand_color = models.CharField(
        _("Brand color"),
        max_length=50, 
        default="#ee5837",
        validators=[
            RegexValidator(
                regex=r"^(#[0-9a-fA-F]{6}|oklch\([\d.]+%? [\d.]+ [\d.]+\))$",
                message=_("Enter a valid HEX color or OKLCH format (e.g., oklch(0.68 0.28 296))")
            )
        ]
    )
    logo = models.ImageField(_("Logo"), upload_to="branding/", null=True, blank=True)
    contact_email = models.EmailField(_("Contact email"), null=True, blank=True)
    contact_phone = models.CharField(_("Contact phone"), max_length=20, null=True, blank=True)
    currency = models.CharField(_("Currency"), max_length=10, default="EUR")
    
    # UI Labels
    event_type_label = models.CharField(_("Event type label"), max_length=50, default="Service Category")
    event_label = models.CharField(_("Event label"), max_length=50, default="Consultation")
    availability_free_label = models.CharField(_("Availability free label"), max_length=50, default="Available")
    availability_regular_label = models.CharField(_("Availability regular label"), max_length=50, default="Partial")
    availability_no_free_label = models.CharField(_("Availability no free label"), max_length=50, default="Fully Booked")
    extras_label = models.CharField(_("Extras label"), max_length=50, default="Add-ons")
    privacy_policy_url = models.URLField(_("Privacy policy URL"), null=True, blank=True)

    def __str__(self):
        return str(_("Company Profile"))

    class Meta:
        verbose_name = _("Company Profile")

# --- Service Catalog ---

class EventTypeGroup(models.Model):
    name = models.CharField(_("Name"), max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Agrupación de servicios")
        verbose_name_plural = _("Agrupaciones de servicios")

class EventType(models.Model):
    PAYMENT_MODELS = [
        ("PRE-PAID", _("Pre-paid")),
        ("POST-PAID", _("Post-paid")),
    ]
    group = models.ForeignKey(EventTypeGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="event_types", verbose_name=_("Agrupación"))
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), null=True, blank=True)
    payment_model = models.CharField(_("Payment model"), max_length=20, choices=PAYMENT_MODELS, default="POST-PAID")
    allow_overlap = models.BooleanField(_("Allow overlap"), default=False)
    image = models.ImageField(_("Image"), upload_to="event_types/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Event Type")
        verbose_name_plural = _("Event Types")

class Event(models.Model):
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name="events", verbose_name=_("Event type"))
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), null=True, blank=True)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(_("Duration (minutes)"))
    image = models.ImageField(_("Image"), upload_to="events/", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

# --- Company Availability ---

class CompanyAvailability(BaseAvailabilityRange):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name="availabilities", default=1, verbose_name=_("Company"))

    class Meta:
        verbose_name = _("Company Availability")
        verbose_name_plural = _("Company Availabilities")

class CompanyWeekdaySlot(BaseAvailabilitySlot):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name="weekday_slots", default=1, verbose_name=_("Company"))

    class Meta:
        verbose_name = _("Company Weekday Slot")
        verbose_name_plural = _("Company Weekday Slots")
        unique_together = ("company", "weekday", "start_time", "end_time")

class CompanyDateOverride(BaseDateOverride):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name="overrides", default=1, verbose_name=_("Company"))

    class Meta:
        verbose_name = _("Company Date Override")
        verbose_name_plural = _("Company Date Overrides")

# --- Event Availability ---

class EventAvailability(BaseAvailabilityRange):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="availabilities", verbose_name=_("Service"))
    
    class Meta:
        verbose_name = _("Service Availability")
        verbose_name_plural = _("Service Availabilities")

class AvailabilitySlot(BaseAvailabilitySlot):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="slots", verbose_name=_("Service"))

    class Meta:
        verbose_name = _("Service Weekday Slot")
        verbose_name_plural = _("Service Weekday Slots")
        unique_together = ("event", "weekday", "start_time", "end_time")

class EventDateOverride(BaseDateOverride):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="overrides", verbose_name=_("Service"))
    
    class Meta:
        verbose_name = _("Service Date Override")
        verbose_name_plural = _("Service Date Overrides")

# --- Booking ---

class Booking(models.Model):
    STATUS_CHOICES = [
        ("PENDING", _("Pending")),
        ("CONFIRMED", _("Confirmed")),
        ("PAID", _("Paid")),
        ("CANCELLED", _("Cancelled")),
    ]
    services = models.ManyToManyField(Event, related_name="bookings", verbose_name=_("Services"))
    start_time = models.DateTimeField(_("Start time"), db_index=True)
    end_time = models.DateTimeField(_("End time"), db_index=True, null=True, blank=True)
    client_name = models.CharField(_("Client name"), max_length=255)
    client_email = models.EmailField(_("Client email"))
    client_phone = models.CharField(_("Client phone"), max_length=20, null=True, blank=True)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default="PENDING", db_index=True)
    special_requests = models.TextField(_("Special requests"), null=True, blank=True)
    google_event_id = models.CharField(_("Google event ID"), max_length=255, null=True, blank=True)
    stripe_payment_id = models.CharField(_("Stripe payment ID"), max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.client_name} - {self.start_time}"

    class Meta:
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def calculate_end_time(self):
        if not self.start_time:
            return None
        
        total_duration = sum(event.duration_minutes for event in self.services.all())
        from datetime import timedelta
        return self.start_time + timedelta(minutes=total_duration)

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from datetime import timedelta

@receiver(m2m_changed, sender=Booking.services.through)
def update_booking_end_time(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        total_duration = sum(event.duration_minutes for event in instance.services.all())
        instance.end_time = instance.start_time + timedelta(minutes=total_duration)
        instance.save(update_fields=["end_time"])
