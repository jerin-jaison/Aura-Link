"""
Management command to create default admin user.
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import User
from apps.plans.models import Plan


class Command(BaseCommand):
    help = 'Create default admin user'
    
    def handle(self, *args, **kwargs):
        email = 'jerinjaison07@gmail.com'
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin user {email} already exists'))
            return
        
        # Get Premium plan
        try:
            premium_plan = Plan.objects.get(name='Premium')
        except Plan.DoesNotExist:
            self.stdout.write(self.style.ERROR('Premium plan not found. Run: python manage.py loaddata initial_plans'))
            return
        
        # Create admin
        admin = User.objects.create_superuser(
            email=email,
            password='123',
            plan=premium_plan
        )
        admin.username = 'admin'
        admin.save()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {email} / 123'))