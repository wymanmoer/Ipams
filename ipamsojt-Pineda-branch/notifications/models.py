from django.db import models
from accounts.models import User, Student, UserRole
from records.models import Record
from ckeditor.fields import RichTextField

# Role Request Student, Role Request Adviser, New Record Proposal/Thesis, New Record Project, Resubmission, Role Request Approved
# Comments, Record Approved, Record Decline 
class NotificationType(models.Model):
    name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='user') #who sent the notification

    course = models.CharField(
        blank=True, default='', null=True, max_length=255
    )  # student course if student 
    recipient = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True, related_name='recipient') #who will receive the notification

    course = models.CharField(blank=True, null=True, max_length=255) # student course if student
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='recipient') #who will receive the notification

    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, blank=True, null=True, default=7, related_name='role') # role of who sent the notification
    record = models.ForeignKey(Record, on_delete=models.CASCADE, blank=True, null=True, related_name='record') # current record if record
    notif_type = models.ForeignKey(NotificationType, on_delete=models.CASCADE, blank=True, null=True, related_name='notif_type') # type of notification
    read_by = models.ManyToManyField(User)
    to_ktto = models.BooleanField(default=False)
    to_rdco = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.notif_type.name