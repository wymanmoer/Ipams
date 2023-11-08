from concurrent.futures import thread
from http.client import INTERNAL_SERVER_ERROR
import json
from threading import Thread
import requests

from django.contrib import messages
from django.contrib.auth import signals, authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import redirect

from ipams import settings
from . import forms
from .decorators import authorized_roles
from .models import User, UserRole, RoleRequest, Course, Student, Log, Setting, College, Department, Adviser, UserRecord
from records.models import CheckedRecord, Record
from notifications.models import Notification, NotificationType
from accounts.auxfunctions import EmailThreading, roleRequestStudent, roleRequestAdviser
from django.db.models import Q, Subquery
from django.contrib.auth.hashers import check_password

from django.views.decorators.csrf import csrf_exempt
from axes.decorators import axes_dispatch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

User = get_user_model()
from .tokens import activation_token

from axes.models import AccessAttempt, AccessBase
from axes.utils import reset

#custom function to check the request type since Httpis_ajax(request=request) method is deprecated.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

# class RegisterView(View):
#     name = 'accounts/register.html'

#     def get(self, request):
#         form = forms.RegistrationForm()
#         return render(request, self.name, {'form': form, 'hide_profile': True})

#     def post(self, request):
#         form = forms.RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_password()
#             if password:
#                 user.set_password(password)
#                 user.save()
#                 login(request, user)
#                 return redirect('/')
#             messages.error(request, 'Password did not match!')
#         else:
#             if not form.cleaned_data.get('username'):
#                 messages.error(request, 'Username not available')
#             elif not form.cleaned_data.get('email'):
#                 messages.error(request, 'That E-mail is already in used by another user')
#             else:
#                 messages.error(request, 'Invalid form')
#         form = forms.RegistrationForm()
#         return render(request, self.name, {'form': form, 'hide_profile': True})

class SignupView(View):
    name = 'accounts/signup.html'

    def get(self, request):
        form = forms.SignupForm()
        return render(request, self.name, {'form': form, 'hide_profile': True})

    def post(self, request):
        if is_ajax(request=request):
            if request.POST.get("get_courses", 'false') == 'true':
                courses = []
                for course in Course.objects.all():
                    courses.append({'value': course.name, 'id': course.pk})
                return JsonResponse({'courses': courses})
            elif request.POST.get("get_colleges", 'false') == 'true':
                colleges = []
                for college in College.objects.all():
                    colleges.append({'value': college.name, 'id': college.pk})
                return JsonResponse({'colleges': colleges})
            elif request.POST.get("get_departments", 'false') == 'true':
                departments = []
                for department in Department.objects.all():
                    departments.append({'value': department.name, 'id': department.pk, 'college': department.college.name})
                return JsonResponse({'departments': departments})
            else:
                return JsonResponse({'success': 'false'})
        else:
            form = forms.SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                password = form.cleaned_password()
                if password:
                    user.set_password(password)
                    user.role = UserRole.objects.get(pk=1)

                    user.is_active = False
                    user.is_verified = False

                    user.save()
                    if request.POST.get('role', '0') == '2':
                        course = json.loads(request.POST.get('course'))
                        Student(user=user, course=Course.objects.get(pk=course[0]['id'])).save()
                        #Student(user=user, course=Course.objects.get(pk=int(course[0]['id']))).save()
                        # course=Course.objects.get(pk=int(course[0]['id']))
                        # roleRequestStudentNotify(user.id, course)
                        roleRequestStudent(request, user.id)
                    elif request.POST.get('role', '0') == '3':
                        college = json.loads(request.POST.get('college'))
                        department = json.loads(request.POST.get('department'))
                        Adviser(user=user, department=Department.objects.get(pk=department[0]['id']), 
                            college=College.objects.get(pk=college[0]['id'])).save()
                        # Adviser(user=user, department=Department.objects.get(pk=int(department[0]['id'])), 
                        #     college=College.objects.get(pk=int(college[0]['id']))).save()
                        # roleRequestAdviserNotify(user.id)
                        roleRequestAdviser(request, user.id)
                    RoleRequest(user=user, role=UserRole.objects.get(pk=request.POST.get('role', 0))).save()
                    #RoleRequest(user=user, role=UserRole.objects.get(pk=int(request.POST.get('role', 0)))).save()
                    
                    #composing the message that will be sent to user email account
                    current_site = get_current_site(request)
                    mail_subject = 'Activate your account.'
                    message = render_to_string(
                        'accounts/account_active_email.html', {
                           'user': user,
                           'domain': current_site.domain,
                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                           'token': default_token_generator.make_token(user), 
                        }
                    )
                    to_email = form.cleaned_data.get('email')
                    email_message = send_mail(
                        mail_subject, 
                        message, 
                        settings.EMAIL_HOST_USER, 
                        [to_email],
                        fail_silently=False
                    )
                    EmailThreading(email_message).start()
                    messages.success(request, 'Activate account by confirming your email address to complete the registration.')

                    # login(request, user)
                    return redirect('/')
                error_message = 'Password did not match!'
            else:
                if not form.cleaned_data.get('username'):
                    error_message = 'Username not available'
                elif not form.cleaned_data.get('email'):
                    error_message = 'That E-mail is already in used by another user'
                else:
                    error_message = 'Invalid form'
            if error_message:
                messages.error(request, error_message)
            # form = forms.RegistrationForm(request.POST)
            return render(request, self.name, {'form': form, 'hide_profile': True})

#For activation of user account through email
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist, ConnectionError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.is_verified = True

        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        messages.success(request, f'Welcome {user.username}. Thank you for your email confirmation. You are now logged in.')
    else:
        messages.error(request, 'Activation link is invalid!')
    return redirect('records-index')

@method_decorator(axes_dispatch, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    name = 'ipams/base.html'

    def get(self, request):
        return render(request, self.name)

    def post(self, request):
        if request.method == 'POST':
            ''' reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
            ''' End reCAPTCHA validation '''

            if result['success'] or settings.TEST_FORM:
                form = forms.LoginForm(request.POST)
                if form.is_valid():
                    username = form.cleaned_data.get('username')
                    user = authenticate(
                        request=request,
                        username=form.cleaned_data.get('username'),
                        password=form.cleaned_data.get('password'),
                    )

                    if user:
                        if user.is_verified:
                            login(request, user)
                            if request.user.role.id == 5: #rdco
                                notifications = Notification.objects.filter(Q(to_rdco=True) | Q(recipient=user.id))
                                request.session['notif_count'] = notifications.count()
                            elif request.user.role.id == 4: #ktto
                                notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id))
                                request.session['notif_count'] = notifications.count()
                            elif request.user.role.id == 3: #adviser
                                notifications = Notification.objects.filter(Q(recipient=user.id) | Q(notif_type=NotificationType.objects.get(pk=6)) | Q(notif_type=NotificationType.objects.get(pk=1)) | Q(notif_type=NotificationType.objects.get(pk=2)))
                                request.session['notif_count'] = notifications.count()
                            elif request.user.role.id == 7: #tbi
                                notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id))
                                request.session['notif_count'] = notifications.count()
                            elif request.user.role.id == 2: #student
                                notifications = Notification.objects.filter(recipient=user.id)
                                request.session['notif_count'] = notifications.count()

                            messages.success(request, f'Welcome {username}')
                            if request.POST.get('next'):
                                return redirect(request.POST.get('next'))
                        else:
                            messages.error(request, 'Account is not activated yet. Please check your email address to verify.')
                    else:
                        messages.error(request, 'Invalid Username/Password')
            else:
                messages.error(request, 'Recaptcha is required')
        return redirect('records-index')

def logout(request):
    auth_logout(request)
    messages.success(request, 'You are now logged out from the system...')
    return redirect('/')


def change_password(request):
    if request.method == 'POST':
        password_old = request.POST.get('password-old', None)
        password_new = request.POST.get('password-new', None)
        if ((password_old is not None or password_old != '') and (password_new is not None or password_new != '')) and len(password_new) >= 8:
            if check_password(password_old, request.user.password):
                request.user.set_password(password_new)
                request.user.save()
                messages.success(request, "Password changed!")
            else:
                messages.error(request, 'Incorrect old password')
        else:
            messages.error(request, 'New password must be 8 characters longer')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@authorized_roles(roles=['adviser', 'ktto', 'rdco', 'itso', 'tbi'])
def get_all_accounts(request):
    if request.method == 'POST':
        accounts = None
        if request.user.role.name == 'Adviser':
            #accounts = User.objects.prefetch_related('role').filter(Q(role=UserRole.objects.get(pk=1)) | Q(role=UserRole.objects.get(pk=2))).prefetch_related('role')
            accounts = User.objects.prefetch_related('role').filter(role__lte=2)
        else:
            accounts = User.objects.prefetch_related('role').all()
        
        data = []
        for account in accounts:
            role = ''
            role_request = RoleRequest.objects.select_related('role').filter(user=account).first()
            if role_request and role_request.role.pk != 1:
                role = f'<a href="#" onclick="acceptRole({account.pk}, {role_request.role.pk})">{role_request.role.name}</a>'
            data.append([
                '',
                account.pk,
                str(account.username),
                f'{account.last_name}, {account.first_name} {account.middle_name}',
                account.role.name,
                role,
            ])
        return JsonResponse({'data': data})

def save_profile(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        contact_no = request.POST.get('contact_no')
        if first_name != '':
            user.first_name = first_name
        if middle_name != '':
            user.middle_name = middle_name
        if last_name != '':
            user.last_name = last_name
        if contact_no != '':
            user.contact_no = contact_no
        user.save()
    return JsonResponse({'message': 'success'})


@authorized_roles(roles=['adviser', 'ktto', 'rdco', 'tbi'])
def get_pending_count(request):
    if request.method == 'POST':
        if request.user.role.id == 3:
            adviser_exclude = CheckedRecord.objects.select_related('record').all()
            new_record_rows = Record.objects.filter(adviser=request.user.pk).exclude(pk__in=Subquery(adviser_exclude.values('record').distinct())).values('pk', 'title')
            delete_request_rows = ''

        elif request.user.role.id == 4 or request.user.role.id == 7:
            ktto_exclude = CheckedRecord.objects.select_related('record').filter(Q(checked_by__in=Subquery(User.objects.filter(role=4).values('pk'))) | Q(checked_by__in=Subquery(User.objects.filter(role=7).values('pk'))))
            ktto_include = CheckedRecord.objects.select_related('record').filter(status='approved', checked_by__in=Subquery(User.objects.filter(role=3).values('pk')))
            # rows = Record.objects.filter(pk__in=Subquery(ktto_include.values('record'))).exclude(pk__in=Subquery(ktto_exclude.values('record'))).values('pk', 'title')
            new_record_rows = Record.objects.filter(pk__in=Subquery(ktto_include.values('record'))).exclude(pk__in=Subquery(ktto_exclude.values('record'))).values('pk', 'title')
            delete_request_rows = Record.objects.filter(is_marked=True)

        elif request.user.role.id == 5:
            rdco_exclude = CheckedRecord.objects.select_related('record').filter(checked_by__in=Subquery(User.objects.filter(role=5).values('pk')))
            rdco_include = CheckedRecord.objects.select_related('record').filter(Q(checked_by__in=Subquery(User.objects.filter(role=4).values('pk'))) | Q(checked_by__in=Subquery(User.objects.filter(role=7).values('pk'))), status='approved')
            # rows = Record.objects.filter(pk__in=Subquery(rdco_include.values('record'))).exclude(pk__in=Subquery(rdco_exclude.values('record'))).values('pk','title')
            new_record_rows = Record.objects.filter(pk__in=Subquery(rdco_include.values('record'))).exclude(pk__in=Subquery(rdco_exclude.values('record'))).values('pk','title')
            delete_request_rows = Record.objects.filter(is_marked=True)

        return JsonResponse({"pending-count": len(new_record_rows) + len(delete_request_rows)})


class HelpView(View):
    name = 'help/index.html'

    def get(self, request):
        return render(request, self.name)


class ManualView(View):
    name = 'help/manual.html'

    def get(self, request):
        return render(request, self.name)


class SettingsView(View):
    name = 'accounts/settings.html'

    @method_decorator(authorized_roles(roles=['ktto', 'rdco', 'tbi']))
    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        context = {
            'landing_page': Setting.objects.get(name='landing_page'),
            'settings_form': forms.SettingsForm(instance=Setting.objects.get(name='landing_page')),
        }
        return render(request, self.name, context)

    def post(self, request):
        settings_form = forms.SettingsForm(request.POST, instance=Setting.objects.get(name='landing_page'))
        if settings_form.is_valid():
            settings_form.save()
        else:
            print('invalid')
        return redirect('accounts-settings')


@authorized_roles(roles=['adviser', 'ktto', 'rdco', 'itso', 'tbi'])
def get_all_locked_accounts(request):
    if request.method == 'POST':
        accounts = AccessAttempt.objects.all()
        data = []
        for account in accounts:
            data.append([
                '',
                account.attempt_time,
                account.username,
                account.failures_since_start
            ])
        return JsonResponse({'data': data})