from django.contrib import admin
from django.contrib.auth.models import Group
from accounts.models import User, UserRecord, UserRole, RoleRequest, Log, Course, Student, Setting, Adviser, Department, College
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


#class UserAdmin(BaseUserAdmin):

admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(RoleRequest)
admin.site.register(UserRecord)
admin.site.register(Log)
admin.site.register(Course)
admin.site.register(Student)
admin.site.unregister(Group)
admin.site.register(Setting)
admin.site.register(Adviser)
admin.site.register(Department)
admin.site.register(College)