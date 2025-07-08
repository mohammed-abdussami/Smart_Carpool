from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile, Schedule, Match, ChatRoom, ChatMessage
from django.utils import timezone
from .utils import calculate_distance, time_difference, find_matches
from scheduler.management.commands.admin_report import Command

# Run the report manually
cmd = Command()
cmd.handle()

class ModelTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')
        
        self.profile1 = UserProfile.objects.create(
            user=self.user1,
            phone_number='1234567890',
            car_available=True,
            car_capacity=3
        )
        
        self.schedule1 = Schedule.objects.create(
            user=self.user1,
            day='Mon',
            start_time=timezone.now().time(),
            end_time=(timezone.now() + timezone.timedelta(hours=1)).time(),
            origin='Location A',
            destination='Location B'
        )

    def test_user_profile_creation(self):
        self.assertEqual(self.profile1.user.username, 'user1')
        self.assertEqual(self.profile1.car_capacity, 3)

    def test_schedule_creation(self):
        self.assertEqual(self.schedule1.day, 'Mon')
        self.assertEqual(self.schedule1.user.username, 'user1')

class UtilityTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        self.schedule1 = Schedule.objects.create(
            user=self.user1,
            day='Mon',
            start_time='08:00:00',
            end_time='09:00:00',
            origin='New York',
            destination='Boston',
            flexible=True
        )
        
        self.schedule2 = Schedule.objects.create(
            user=self.user2,
            day='Mon',
            start_time='08:30:00',
            end_time='09:30:00',
            origin='Newark',
            destination='Cambridge',
            flexible=False
        )

    def test_time_difference_calculation(self):
        time1 = timezone.now().replace(hour=8, minute=0).time()
        time2 = timezone.now().replace(hour=8, minute=30).time()
        diff = time_difference(time1, time2)
        self.assertEqual(diff, 30)

    def test_find_matches(self):
        matches = find_matches(self.schedule1)
        self.assertGreaterEqual(len(matches), 1)
        
        # Test the match with our second schedule
        found = False
        for match in matches:
            if match['schedule'].id == self.schedule2.id:
                found = True
                self.assertLess(match['score'], 100)  # Score should be reasonable
                break
        self.assertTrue(found)


from django.core.mail import send_mail

class EmailTests(TestCase):
    def test_email_sending(self):
        # Test email sending
        send_mail(
            'Test Subject - Carpool Admin', 
            'This confirms your email settings are working!',
            '160422733078@mjcollege.ac.in',
            ['160422733078@mjcollege.ac.in'],
            fail_silently=False,
        )

class AdminUserCreationTests(TestCase):
    def setUp(self):
        # Make sure user is unique for every test run
        User.objects.filter(username='testadmin').delete()
        self.admin_user = User.objects.create_user(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_admin_user_created(self):
        self.assertTrue(User.objects.filter(username='testadmin').exists())
