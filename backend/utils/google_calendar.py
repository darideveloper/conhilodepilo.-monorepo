import json
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_google_calendar_service():
    if not settings.GOOGLE_SERVICE_ACCOUNT_JSON or not settings.GOOGLE_CALENDAR_ID:
        return None

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        credentials_info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info, scopes=SCOPES
        )
        return build("calendar", "v3", credentials=credentials)
    except Exception as e:
        logger.error("Failed to build Google Calendar service: %s", e)
        return None


def booking_to_event_body(booking):
    service_names = ", ".join(s.name for s in booking.services.all())
    price_total = sum(s.price for s in booking.services.all())

    description_parts = [f"Servicios: {service_names}", f"Precio total: {price_total}"]
    if booking.client_phone:
        description_parts.append(f"Teléfono: {booking.client_phone}")
    if booking.special_requests:
        description_parts.append(f"Solicitudes especiales: {booking.special_requests}")
    description_parts.append(f"Estado: {booking.get_status_display()}")

    local_start = timezone.localtime(booking.start_time)
    local_end = timezone.localtime(booking.end_time)

    return {
        "summary": f"{booking.client_name} — {service_names}",
        "description": "\n".join(description_parts),
        "start": {"dateTime": local_start.isoformat(), "timeZone": settings.TIME_ZONE},
        "end": {"dateTime": local_end.isoformat(), "timeZone": settings.TIME_ZONE},
    }


def sync_booking_to_google(booking):
    if not settings.GOOGLE_CALENDAR_ID or not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        booking.__class__.objects.filter(pk=booking.pk).update(
            google_sync_status="DISABLED",
            google_sync_error="",
        )
        return

    service = get_google_calendar_service()
    if service is None:
        booking.__class__.objects.filter(pk=booking.pk).update(
            google_sync_status="FAILURE",
            google_sync_error="Could not initialize Google Calendar service.",
        )
        return

    event_body = booking_to_event_body(booking)
    calendar_id = settings.GOOGLE_CALENDAR_ID

    try:
        if booking.google_event_id:
            try:
                result = (
                    service.events()
                    .patch(
                        calendarId=calendar_id,
                        eventId=booking.google_event_id,
                        body=event_body,
                        sendUpdates="none",
                    )
                    .execute()
                )
            except Exception as e:
                from googleapiclient.errors import HttpError
                if isinstance(e, HttpError) and e.resp.status == 404:
                    result = (
                        service.events()
                        .insert(
                            calendarId=calendar_id,
                            body=event_body,
                            sendUpdates="none",
                        )
                        .execute()
                    )
                else:
                    raise
        else:
            result = (
                service.events()
                .insert(
                    calendarId=calendar_id,
                    body=event_body,
                    sendUpdates="none",
                )
                .execute()
            )

        booking.google_event_id = result.get("id")
        booking.google_sync_status = "SUCCESS"
        booking.google_sync_error = ""
        booking.last_synced_at = timezone.now()

        booking.__class__.objects.filter(pk=booking.pk).update(
            google_event_id=booking.google_event_id,
            google_sync_status=booking.google_sync_status,
            google_sync_error=booking.google_sync_error,
            last_synced_at=booking.last_synced_at,
        )

    except Exception as e:
        logger.error("Google Calendar sync failed for booking %s: %s", booking.pk, e)
        booking.google_sync_status = "FAILURE"
        booking.google_sync_error = str(e)[:1000]
        booking.__class__.objects.filter(pk=booking.pk).update(
            google_sync_status=booking.google_sync_status,
            google_sync_error=booking.google_sync_error,
        )


def delete_google_calendar_event(booking):
    if not booking.google_event_id:
        return

    if not settings.GOOGLE_CALENDAR_ID or not settings.GOOGLE_SERVICE_ACCOUNT_JSON:
        return

    service = get_google_calendar_service()
    if service is None:
        return

    try:
        service.events().delete(
            calendarId=settings.GOOGLE_CALENDAR_ID,
            eventId=booking.google_event_id,
            sendUpdates="none",
        ).execute()
    except Exception as e:
        logger.error(
            "Google Calendar delete failed for booking %s (event %s): %s",
            booking.pk,
            booking.google_event_id,
            e,
        )
