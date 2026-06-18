import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser/admin from environment variables ADMIN_USERNAME, ADMIN_PASSWORD, and ADMIN_EMAIL'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME')
        password = os.getenv('ADMIN_PASSWORD')
        email = os.getenv('ADMIN_EMAIL', 'admin@aura.com')

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_USERNAME or ADMIN_PASSWORD not set in environment. Skipping admin creation.'
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'role': 'admin',
                'is_superuser': True,
                'is_staff': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {username}'))
        else:
            user.set_password(password)
            user.role = 'admin'
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user {username} already exists. Updated password and roles.'))
