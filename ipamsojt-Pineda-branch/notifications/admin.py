from django.contrib import admin

# Register your models here.
from notifications.models import Notification, NotificationType

admin.site.register(Notification)
admin.site.register(NotificationType)