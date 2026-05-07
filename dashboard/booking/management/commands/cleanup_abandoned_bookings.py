from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from booking.models import Booking

class Command(BaseCommand):
    help = 'Cleans up abandoned pending Stripe Checkout bookings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run the cleanup without deleting any records.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        ttl_hours = settings.STRIPE_PENDING_BOOKING_TTL_HOURS
        cutoff_time = timezone.now() - timedelta(hours=ttl_hours)

        abandoned_bookings = Booking.objects.filter(
            status='PENDING',
            created_at__lt=cutoff_time
        )
        
        count = abandoned_bookings.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No abandoned bookings found to clean up.'))
            return
            
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'[DRY RUN] Would delete {count} abandoned booking(s).'))
        else:
            abandoned_bookings.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} abandoned booking(s).'))
