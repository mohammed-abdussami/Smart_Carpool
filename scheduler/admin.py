from django.contrib import admin
from .models import UserProfile, Schedule, Match
from django.conf import settings

# Check admin emails
print("Admin emails:", settings.ADMINS)

# Verify email settings
print("Email host:", settings.EMAIL_HOST)
print("Email port:", settings.EMAIL_PORT)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'car_available', 'car_capacity', 'is_admin')
    list_filter = ['car_available']
    search_fields = ('user__username', 'phone_number')
    def is_admin(self, obj):
        return obj.user.is_staff 
    is_admin.boolean = True
    pass

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'day', 'start_time', 'end_time', 'origin', 'destination')
    list_filter = ('day', 'user')
    search_fields = ('user__username', 'origin', 'destination')

class MatchAdmin(admin.ModelAdmin):
    list_display = ('schedule1', 'schedule2', 'status', 'score', 'created_at')
    list_filter = ('status',)
    search_fields = ('schedule1__user__username', 'schedule2__user__username')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Match, MatchAdmin)