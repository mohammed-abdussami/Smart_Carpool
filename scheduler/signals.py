# scheduler/signals.py
from django.core.mail import mail_admins
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from smtplib import SMTPException

@receiver(post_save, sender=User)
def send_user_notification(sender, instance, created, **kwargs):
    if created:
        subject = f'New User Registration: {instance.username}'
        message = render_to_string('admin/user_registered_email.html', {
            'user': instance,
            'time': instance.date_joined
        })
        mail_admins(subject, message, html_message=message)

def send_user_notification(sender, instance, created, **kwargs):
    if created:
        try:
            subject = f"New user created: {instance.username}"
            message = f"A new user was created: {instance.email}"
            mail_admins(subject, message, html_message=message, fail_silently=True)
        except SMTPException:
            pass