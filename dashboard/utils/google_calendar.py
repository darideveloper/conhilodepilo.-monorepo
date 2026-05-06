import json
import logging
import time
import socket
import ssl
from django.conf import settings
from django.utils import timezone
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def _call_with_retry(callable_factory, *, attempts=3, backoff=(1, 2, 4)):
    """
    Retries on transient errors (5xx, socket, SSL).
    callable_factory: a lambda/function that returns an executable request.
    """
    for i in range(attempts):
        try:
            return callable_factory().execute()
        except (socket.error, ssl.SSLError) as e:
            if i == attempts - 1:
                raise
            time.sleep(backoff[i])
        except HttpError as e:
            if i == attempts - 1 or e.resp.status < 500:
                raise
            time.sleep(backoff[i])
        except Exception as e:
            # httplib2.HttpLib2Error and others might be buried
            if "HttpLib2Error" in type(e).__name__:
                if i == attempts - 1:
                    raise
                time.sleep(backoff[i])
            else:
                raise


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
        return build("calendar", "v3", credentials=credentials, cache_discovery=False)
    except Exception as e:
        logger.error("Failed to build Google Calendar service: %s", e)
        return None


def booking_to_event_body(booking):
    service_names = ", ".join(s.name for s in booking.services.all())
    price_total = sum(s.price for s in booking.services.all())

    summary = f"{booking.client_name} — {service_names}"
    if booking.status == "CANCELLED":
        if not summary.startswith("[CANCELLED] "):
            summary = f"[CANCELLED] {summary}"

    description_parts = [
        f"Cliente: {booking.client_name} ({booking.client_email})",
        f"Servicios: {service_names}",
        f"Precio total: {price_total}",
    ]
    if booking.client_phone:
        description_parts.append(f"Teléfono: {booking.client_phone}")
    if booking.special_requests:
        description_parts.append(f"Solicitudes especiales: {booking.special_requests}")
    description_parts.append(f"Estado: {booking.get_status_display()}")

    local_start = timezone.localtime(booking.start_time)
    local_end = timezone.localtime(booking.end_time)

    host_domain = getattr(settings, "HOST_DOMAIN", "conhilorepilo.com")

    return {
        "summary": summary,
        "description": "\n".join(description_parts),
        "start": {"dateTime": local_start.isoformat(), "timeZone": settings.TIME_ZONE},
        "end": {"dateTime": local_end.isoformat(), "timeZone": settings.TIME_ZONE},
        "extendedProperties": {
            "private": {
                "booking_id": str(booking.pk),
            }
        },
        "iCalUID": f"booking-{booking.pk}@{host_domain}",
    }


def format_google_error(e):
    if isinstance(e, HttpError):
        try:
            content = json.loads(e.content.decode("utf-8"))
            detail = content.get("error", {}).get("message", str(e))
        except Exception:
            detail = str(e)
        return f"{e.resp.status} {e.resp.reason}: {detail}"
    return f"{type(e).__name__}: {str(e)}"


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
        # Idempotency: look up by booking_id if google_event_id is missing
        if not booking.google_event_id:
            results = _call_with_retry(
                lambda: service.events().list(
                    calendarId=calendar_id,
                    privateExtendedProperty=f"booking_id={booking.pk}",
                    showDeleted=False,
                    maxResults=1,
                )
            )
            items = results.get("items", [])
            if items:
                booking.google_event_id = items[0]["id"]

        if booking.google_event_id:
            try:
                result = _call_with_retry(
                    lambda: service.events().patch(
                        calendarId=calendar_id,
                        eventId=booking.google_event_id,
                        body=event_body,
                        sendUpdates="none",
                    )
                )
            except HttpError as e:
                if e.resp.status == 404:
                    # Event was deleted from calendar side, re-insert
                    result = _call_with_retry(
                        lambda: service.events().insert(
                            calendarId=calendar_id,
                            body=event_body,
                            sendUpdates="none",
                        )
                    )
                else:
                    raise
        else:
            result = _call_with_retry(
                lambda: service.events().insert(
                    calendarId=calendar_id,
                    body=event_body,
                    sendUpdates="none",
                )
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
        error_msg = format_google_error(e)
        logger.error(
            "Google Calendar sync failed for booking %s: %s", booking.pk, error_msg
        )
        booking.google_sync_status = "FAILURE"
        booking.google_sync_error = error_msg[:1000]
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
        _call_with_retry(
            lambda: service.events().delete(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                eventId=booking.google_event_id,
                sendUpdates="none",
            )
        )
    except HttpError as e:
        if e.resp.status in (404, 410):
            # Already deleted
            return
        error_msg = format_google_error(e)
        logger.error(
            "Google Calendar delete failed for booking %s (event %s): %s",
            booking.pk,
            booking.google_event_id,
            error_msg,
        )
    except Exception as e:
        error_msg = format_google_error(e)
        logger.error(
            "Google Calendar delete failed for booking %s (event %s): %s",
            booking.pk,
            booking.google_event_id,
            error_msg,
        )
