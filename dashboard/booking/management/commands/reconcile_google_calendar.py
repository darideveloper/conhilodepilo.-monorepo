from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import F
from django.utils import timezone
from booking.models import Booking
from utils.google_calendar import sync_booking_to_google, get_google_calendar_service


class Command(BaseCommand):
    help = "Reconciles local bookings with Google Calendar events."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: No changes will be applied."))

        # Pass 1: Retry failures
        failures = Booking.objects.filter(google_sync_status="FAILURE")
        failure_count = failures.count()
        if not dry_run:
            for booking in failures:
                sync_booking_to_google(booking)

        # Pass 2: Re-sync drift
        drift = Booking.objects.filter(
            google_sync_status="SUCCESS", last_synced_at__lt=F("updated_at")
        )
        drift_count = drift.count()
        if not dry_run:
            for booking in drift:
                sync_booking_to_google(booking)

        # Pass 3: Report orphans
        orphan_count = 0
        service = get_google_calendar_service()
        if service:
            calendar_id = settings.GOOGLE_CALENDAR_ID
            page_token = None
            while True:
                events_result = (
                    service.events()
                    .list(
                        calendarId=calendar_id,
                        pageToken=page_token,
                        showDeleted=False,
                    )
                    .execute()
                )
                events = events_result.get("items", [])
                for event in events:
                    extended_props = event.get("extendedProperties", {})
                    private_props = extended_props.get("private", {})
                    booking_id = private_props.get("booking_id")

                    if booking_id:
                        if not Booking.objects.filter(pk=booking_id).exists():
                            orphan_count += 1
                            self.stdout.write(
                                self.style.NOTICE(
                                    f"Orphan event found: {event.get('id')} (Booking {booking_id})"
                                )
                            )

                page_token = events_result.get("nextPageToken")
                if not page_token:
                    break

        self.stdout.write(
            self.style.SUCCESS(
                f"Reconciliation summary: {failure_count} failures retried, "
                f"{drift_count} drift fixed, {orphan_count} orphans reported."
            )
        )
