from email.message import EmailMessage
from notifications.models import Notification, NotificationType
from .models import UserRole, User, Student
from datetime import datetime as dt
from django.contrib import messages

from django.core.mail import send_mail, send_mass_mail, EmailMultiAlternatives
from django.db.models import Subquery, Q
from ipams import settings
from threading import Thread

# request to be student method
# def roleRequestStudentNotify(userID, course):
# 	user = User.objects.get(pk=userID)
# 	print(user.first_name)
# 	course = user.student.course.name
# 	notification = Notification(user=user, course=course, role=UserRole.objects.get(pk=2), 
# 		to_ktto=True, to_rdco=True, notif_type=NotificationType.objects.get(pk=1), is_read=False, date_created=dt.now())
	
# 	notification.save()

class EmailThreading(Thread):
	def __init__(self, email_message):
		self.email_message = email_message
		Thread.__init__(self)

	def run(self):
		self.email_message

class EmailThreadingStudent(Thread):
	def __init__(self, email_message_student):
		self.email_message_student = email_message_student
		Thread.__init__(self)

	def run(self):
		self.email_message_student	

class EmailThreadingAdviser(Thread):
	def __init__(self, email_message_adviser):
		self.email_message_adviser = email_message_adviser
		Thread.__init__(self)

	def run(self):
		self.email_message_adviser

def roleRequestStudent(request, userID):
	user = User.objects.get(pk=userID)
	kart_accounts = User.objects.filter(role=3).select_related('role')
	#kart_accounts = User.objects.filter(role__in=Subquery(UserRole.objects.filter(pk=4).values('pk')))

	messages.success(request, "Role Request to be a student sent")
	url = request.build_absolute_uri()
	base_url = url.split("account/signup")
	redirect_path = base_url[0]
	# mail_subject = 'Role Request Student'
	# message = (
	# 			f' {user.first_name} {user.last_name} created an account and requested to be a Student under the program {user.student.course.name}.' \
	# 			f' \nTo accept the role request of the user, login to the website {redirect_path}.'
	# 		)

	# for account in kart_accounts:
	# 	email_message_student = send_mail(
	# 		mail_subject,
	# 		message,
	# 		settings.EMAIL_HOST_USER,
	# 		[account.email]
	# 	)
	# EmailThreadingStudent(email_message_student).start()

	# kart_accounts = User.objects.filter(Q(role__in=Subquery(UserRole.objects.filter(pk=3).values('pk'))) | Q(role__in=Subquery(UserRole.objects.filter(pk=4).values('pk'))) | Q(role__in=Subquery(UserRole.objects.filter(pk=5).values('pk'))) | Q(role__in=Subquery(UserRole.objects.filter(pk=7).values('pk'))))

	mail_subject = 'Role Request Student'
	message = (
		f' {user.first_name} {user.last_name} created an account and requested to be a Student under the program {user.student.course.name}.' \
		f' \nTo accept the role request of the user, login to the website {redirect_path}.'
	)

	messages_to_send = [(mail_subject, message, settings.EMAIL_HOST_USER, [account.email]) for account in kart_accounts]
	email_message_student = send_mass_mail(messages_to_send)
	EmailThreadingStudent(email_message_student).start()

# request to be adviser method
# def roleRequestAdviserNotify(userID):
# 	user = User.objects.get(pk=userID)
# 	print(user.first_name)

# 	notification = Notification(user=user, role=UserRole.objects.get(pk=3), 
# 		to_ktto=True, to_rdco=True, notif_type=NotificationType.objects.get(pk=2), is_read=False, date_created=dt.now())

# 	notification.save()

def roleRequestAdviser(request, userID):
	user = User.objects.get(pk=userID)

	#kart_accounts = User.objects.filter(role__gte=4).select_related('role')
	kart_accounts = User.objects.filter(role__in=['4','5']).select_related('role')
	messages.success(request, "Role Request to be an adviser sent")

	url = request.build_absolute_uri()
	base_url = url.split("account/signup")
	redirect_path = base_url[0]

	# mail_subject = 'Role Request Adviser'
	# message = (
	# 	f' {user.first_name} {user.last_name} created an account and requested to be an Adviser' \
	# 	f' under the department of {user.adviser.department.name} and college of {user.adviser.college.name}.' \
	# 	f' \nTo accept the role request of the user, login to the website {redirect_path}.'
	# )

	# for account in kart_accounts:
	# 	email_message_adviser = send_mass_mail(
	# 		mail_subject,
	# 		message,
	# 		settings.EMAIL_HOST_USER,
	# 		[account.email]
	# 	)
	# EmailThreadingAdviser(email_message_adviser).start()

	# kart_accounts = User.objects.filter(Q(role__in=Subquery(UserRole.objects.filter(pk=3).values('pk'))) | Q(role__in=Subquery(UserRole.objects.filter(pk=4).values('pk'))) | Q(role__in=Subquery(UserRole.objects.filter(pk=5).values('pk'))) | Q(role__in=Subquery(UserRole.objects.filter(pk=7).values('pk'))))
	
	mail_subject = 'Role Request Adviser'
	message = (
		f' {user.first_name} {user.last_name} created an account and requested to be an Adviser' \
		f' under the department of {user.adviser.department.name} and college of {user.adviser.college.name}.' \
		f' \nTo accept the role request of the user, login to the website {redirect_path}.'
	)

	messages_to_send = [(mail_subject, message, settings.EMAIL_HOST_USER, [account.email]) for account in kart_accounts]
	email_message_adviser = send_mass_mail(messages_to_send)
	EmailThreadingAdviser(email_message_adviser).start()