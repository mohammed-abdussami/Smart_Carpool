from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Prints a basic user summary to console'

    def handle(self, *args, **options):
        total = User.objects.count()
        yesterday = datetime.now() - timedelta(days=1)
        new_users = User.objects.filter(date_joined__gte=yesterday)
        self.stdout.write(self.style.SUCCESS(f'Total users: {total}'))
        self.stdout.write(self.style.SUCCESS(f'New in last 24h: {new_users.count()}'))