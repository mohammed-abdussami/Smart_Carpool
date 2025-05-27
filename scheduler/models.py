from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    car_available = models.BooleanField(default=False)
    car_capacity = models.PositiveIntegerField(default=1)
    license_plate = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Schedule(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    flexible = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s {self.day} schedule"

class Match(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    schedule1 = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='schedule1')
    schedule2 = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='schedule2')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    score = models.FloatField(default=0)

    class Meta:
        unique_together = ('schedule1', 'schedule2')

    def __str__(self):
        return f"Match between {self.schedule1.user} and {self.schedule2.user}"

class ChatRoom(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for Match {self.match.id}"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}..."
    