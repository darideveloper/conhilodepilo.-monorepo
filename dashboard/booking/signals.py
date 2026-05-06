from django.db import transaction
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from datetime import timedelta
from .models import Booking
from utils.google_calendar import sync_booking_to_google, delete_google_calendar_event


@receiver(m2m_changed, sender=Booking.services.through)
def update_booking_end_time(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        total_duration = sum(event.duration_minutes for event in instance.services.all())
        instance.end_time = instance.start_time + timedelta(minutes=total_duration)
        instance.save(update_fields=["end_time"])

        # Sync on service changes if not pending
        if instance.status != "PENDING" and instance.services.exists():
            transaction.on_commit(lambda: sync_booking_to_google(instance))


@receiver(post_save, sender=Booking)
def booking_post_save(sender, instance, created, **kwargs):
    # Skip sync if ONLY internal Google fields or end_time are updated.
    # end_time is in the skip-set because the m2m_changed handler and
    # Booking.save()'s recomputation both save with update_fields containing end_time.
    # m2m_changed is the primary sync trigger for service/time changes.
    skip_fields = {
        "google_event_id",
        "google_sync_status",
        "google_sync_error",
        "last_synced_at",
        "end_time",
    }
    if kwargs.get("update_fields") and set(kwargs["update_fields"]) <= skip_fields:
        return

    # Transition to CANCELLED
    if (
        instance.status == "CANCELLED"
        and instance._initial_status != "CANCELLED"
        and instance.google_event_id
    ):
        transaction.on_commit(lambda: sync_booking_to_google(instance))
        return

    # Skip sync if status is PENDING.
    # We only sync when confirmed or paid.
    if instance.status == "PENDING":
        return

    # Otherwise, schedule sync
    transaction.on_commit(lambda: sync_booking_to_google(instance))


@receiver(post_delete, sender=Booking)
def booking_post_delete(sender, instance, **kwargs):
    delete_google_calendar_event(instance)
