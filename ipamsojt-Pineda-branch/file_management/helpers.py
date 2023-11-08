# yourapp/helpers.py

from django.utils import timezone
from .models import LoginEvent

def count_currently_logged_in_users():
    # Count the users who have not logged out
    logged_in_users_count = LoginEvent.objects.filter(log_out_time__isnull=True).count()
    return logged_in_users_count
