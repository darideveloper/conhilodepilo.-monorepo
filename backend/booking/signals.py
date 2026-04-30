from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking


@receiver(post_save, sender=Booking)
def booking_post_save(sender, instance, created, **kwargs):
    # 1. Skip sync on initial creation. 
    # We wait for the m2m_changed signal to trigger a save with services.
    if created:
        return

    # 2. Skip sync if ONLY internal Google fields or end_time are updated
    # BUT we must allow sync if services/price might have changed.
    # Actually, the most reliable way to prevent redundant syncs is checking what changed.
    if kwargs.get("update_fields") and set(kwargs["update_fields"]) <= {
        "google_event_id", "google_sync_status", "google_sync_error", "last_synced_at"
    }:
        return

    # 3. Skip sync if status is PENDING.
    # We only sync when confirmed or paid.
    if instance.status == 'PENDING':
        return

    from utils.google_calendar import sync_booking_to_google
    sync_booking_to_google(instance)


@receiver(post_delete, sender=Booking)
def booking_post_delete(sender, instance, **kwargs):
    from utils.google_calendar import delete_google_calendar_event
    delete_google_calendar_event(instance)
