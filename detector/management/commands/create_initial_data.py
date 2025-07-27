from django.core.management.base import BaseCommand
from detector.models import ThreatCategory, RiskLevel

class Command(BaseCommand):
    help = 'Create initial threat categories and risk levels'

    def handle(self, *args, **options):
        # Create threat categories
        categories = [
            {
                'name': 'Financial Fraud',
                'description': 'Banking and payment fraud attempts',
                'color': '#ef4444',
                'icon': 'bank'
            },
            {
                'name': 'Credential Theft',
                'description': 'Password and login credential theft',
                'color': '#f59e0b',
                'icon': 'key'
            },
            {
                'name': 'Malware Distribution',
                'description': 'Malicious software distribution',
                'color': '#8b5cf6',
                'icon': 'virus'
            },
            {
                'name': 'Social Engineering',
                'description': 'Social engineering attacks',
                'color': '#ec4899',
                'icon': 'user'
            },
            {
                'name': 'Suspicious Activity',
                'description': 'General suspicious behavior',
                'color': '#6b7280',
                'icon': 'warning'
            },
        ]

        for cat_data in categories:
            category, created = ThreatCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created threat category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Threat category already exists: {category.name}')
                )

        # Create risk levels
        risk_levels = [
            {
                'name': 'Low',
                'level': 1,
                'color': '#10b981',
                'description': 'Minimal risk - standard security measures sufficient'
            },
            {
                'name': 'Medium',
                'level': 2,
                'color': '#f59e0b',
                'description': 'Moderate risk - additional monitoring recommended'
            },
            {
                'name': 'High',
                'level': 3,
                'color': '#f97316',
                'description': 'High risk - immediate action required'
            },
            {
                'name': 'Critical',
                'level': 4,
                'color': '#ef4444',
                'description': 'Critical risk - emergency response needed'
            },
        ]

        for risk_data in risk_levels:
            risk_level, created = RiskLevel.objects.get_or_create(
                name=risk_data['name'],
                defaults=risk_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created risk level: {risk_level.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Risk level already exists: {risk_level.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created initial data!')
        ) 