from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Schedule, Match, ChatRoom, ChatMessage
from django.conf import settings

# Custom User Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

# Other Model Admins
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'car_available', 'car_capacity')
    list_filter = ['car_available']
    search_fields = ('user__email', 'phone_number')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'day', 'start_time', 'end_time', 'origin', 'destination')
    list_filter = ('day',)
    search_fields = ('user__email', 'origin', 'destination')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('schedule1', 'schedule2', 'status', 'score', 'created_at')
    list_filter = ('status',)
    search_fields = ('schedule1__user__email', 'schedule2__user__email')

# ChatRoom Admin
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('match', 'created_at')
    search_fields = ('match__schedule1__user__email', 'match__schedule2__user__email')

# ChatMessage Admin
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'timestamp', 'message_preview')
    list_filter = ('timestamp',)
    search_fields = ('sender__email', 'message')
    
    def message_preview(self, obj):
        return obj.message[:35]
    message_preview.short_description = 'Message Preview'
