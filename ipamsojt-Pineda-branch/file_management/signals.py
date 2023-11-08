# yourapp/signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginEvent

@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    # Create a LoginEvent instance for the logged-in user
    LoginEvent.objects.create(user=user)
