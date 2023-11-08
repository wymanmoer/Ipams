from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from records.models import Record
from accounts.models import User, UserRole
from django.utils.html import format_html
class Folder(models.Model):
    name = models.CharField(max_length=255)
    classification = models.ForeignKey('records.Classification', null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name

class File(models.Model):
    username = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.name

class Subfolder(models.Model):
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='subfolders')
    pscedclassification = models.ForeignKey('records.PSCEDClassification', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class LoginEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now=True)
    log_out_time = models.DateTimeField(null=True, blank=True)

    # def __str__(self):
    #     if self.log_out_time:
    #         return format_html("User: <strong>{}</strong> logged in at {} and logged out at {}",
    #                            self.user.username, self.login_time, self.log_out_time)
    #     else:
    #         return format_html("User: <strong>{}</strong> logged in at {}", self.user.username, self.login_time)

class RecordAccessEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    access_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Accessed Record: {self.record.id} (User: {self.user.username}) at {self.access_time}"


class DeletedFileEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    delete_file_name = models.CharField(max_length=255, default='')  # Update the field name
    delete_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Deleted File: {self.delete_file_name} by User: {self.user.username} (Record: {self.record.id}) at {self.access_time}"


class UploadCount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    upload_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Upload Count for {self.user.username} on Record {self.record.id}"

class FileRenameEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    old_file_name = models.CharField(max_length=255)
    new_file_name = models.CharField(max_length=255)
    rename_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"File Rename Event: User {self.user.username} renamed '{self.old_file_name}' to '{self.new_file_name}' on Record {self.record.id}"


class DownloadEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    downloaded_file_name = models.CharField(max_length=255)
    downloaded_date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f'{self.user.username} downloaded {self.downloaded_file_name} on record {self.record.id}'

class StudentFolder(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming you have a User model
    record = models.ForeignKey(Record, on_delete=models.SET_NULL, null=True, blank=True, related_name="records")
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)