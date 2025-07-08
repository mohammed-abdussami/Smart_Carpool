from django.core.management.base import BaseCommand
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Sends daily admin report'

    def handle(self, *args, **options):
        # Calculate time range
        yesterday = datetime.now() - timedelta(days=1)
        
        # Get stats
        new_users = User.objects.filter(date_joined__gte=yesterday)
        total_users = User.objects.count()
        
        # Prepare email
        subject = f'Daily Report - {datetime.now().strftime("%Y-%m-%d")}'
        message = f'''
        Daily Activity Report:
        
        New Registrations (last 24h): {new_users.count()}
        Total Users: {User.objects.count()}
        
        New Users:
        {", ".join([f"{u.username} ({u.email})" for u in new_users])}
        '''
        
        # Send email
        mail_admins(subject, message)
        self.stdout.write(self.style.SUCCESS('Successfully sent daily report'))
    