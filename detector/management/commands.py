from django.core.management.base import BaseCommand
from detector.models import PredictionHistory
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Clear prediction history with various options'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Delete all prediction history',
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['email', 'sms', 'url'],
            help='Delete history for specific type (email, sms, url)',
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Delete history older than specified days',
        )
        parser.add_argument(
            '--older-than',
            type=int,
            help='Delete history older than specified hours',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        queryset = PredictionHistory.objects.all()
        initial_count = queryset.count()
        
        if options['all']:
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(f'Would delete ALL {initial_count} prediction records')
                )
                return
            deleted_count = queryset.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} prediction records')
            )
            
        elif options['type']:
            queryset = queryset.filter(prediction_type=options['type'])
            count = queryset.count()
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(f'Would delete {count} {options["type"]} prediction records')
                )
                return
            deleted_count = queryset.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} {options["type"]} prediction records')
            )
            
        elif options['days']:
            cutoff_date = timezone.now() - timedelta(days=options['days'])
            queryset = queryset.filter(timestamp__lt=cutoff_date)
            count = queryset.count()
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(f'Would delete {count} prediction records older than {options["days"]} days')
                )
                return
            deleted_count = queryset.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} prediction records older than {options["days"]} days')
            )
            
        elif options['older_than']:
            cutoff_date = timezone.now() - timedelta(hours=options['older_than'])
            queryset = queryset.filter(timestamp__lt=cutoff_date)
            count = queryset.count()
            if options['dry_run']:
                self.stdout.write(
                    self.style.WARNING(f'Would delete {count} prediction records older than {options["older_than"]} hours')
                )
                return
            deleted_count = queryset.delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted_count} prediction records older than {options["older_than"]} hours')
            )
            
        else:
            self.stdout.write(
                self.style.ERROR('Please specify an option: --all, --type, --days, or --older-than')
            )
            self.stdout.write('Use --help for more information') 