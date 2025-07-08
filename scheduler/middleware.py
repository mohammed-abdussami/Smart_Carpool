import logging
from django.core.mail import mail_admins

logger = logging.getLogger('login_logger')

class LoginNotificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated and request.path == '/login/':
            subject = f'User Login: {request.user.username}'
            message = f"""

            Login Activity
            User {request.user.username} ({request.user.email}) logged in.
            IP: {request.META.get('REMOTE_ADDR')}
            User-Agent: {request.META.get('HTTP_USER_AGENT')}
            """
            logger.info(message)
            mail_admins(subject, message)
            
        return response