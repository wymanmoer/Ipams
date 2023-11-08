from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from accounts.decorators import authorized_roles, authorized_record_user
from django.db.models import Count, Subquery, Q, Sum

from accounts.models import User, Student, Course, UserRecord, UserRole, RoleRequest
from records.models import CheckedRecord
from .models import *
from notifications.auxfunctions import *
from records.auxfunctions import *

import datetime

class StudentNotification(View):
    name = 'notifications/student_notification_page.html'

    @method_decorator(authorized_roles(roles=['student']))
    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(recipient=user.id).order_by('-date_created')
        request.session['notif_count'] = notifications.count()
        return render(request, self.name, notificationDisplayStudent(request, notifications, 'Filter'))
    def post(self, request):
        if request.method == 'POST':
            user = request.user
            # for filter
            if 'all' in request.POST:
                notifications = Notification.objects.filter(recipient=user.id).order_by('-date_created')
                return render(request, self.name, filterHelperStudent(request, notifications, 'ALL'))
            elif 'read' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(is_read=True)).order_by('-date_created')
                return render(request, self.name, filterHelperStudent(request, notifications, 'Read'))
            elif 'unread' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(is_read=False)).order_by('-date_created')
                return render(request, self.name, filterHelperStudent(request, notifications, 'Unread'))
            elif 'approved' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(notif_type=NotificationType.objects.get(pk=8))).order_by('-date_created')
                return render(request, self.name, filterHelperStudent(request, notifications, 'Approved'))
            elif 'declined' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(notif_type=NotificationType.objects.get(pk=9))).order_by('-date_created')
                return render(request, self.name, filterHelperStudent(request, notifications, 'Declined'))

            if request.POST.get('removeNotification'):
                idList = request.POST.getlist('listOfID[]')
                for id in idList:
                    Notification.objects.get(pk=id).delete()
                return JsonResponse({'success': True})

            # content for each notification -> 2nd box content
            if request.POST.get('displayContent'):
                id = request.POST.get('notifID')
                Notification.objects.filter(pk=id).update(is_read=True)
                notifications = Notification.objects.filter(recipient=user.id)
                request.session['notif_count'] = notifications.count()
                notif = Notification.objects.get(pk=id)
                if notif.notif_type.name == 'Record Approved' or notif.notif_type.name == 'Record Decline':
                    record_status = CheckedRecord.objects.filter(record=notif.record_id).latest('status')
                    return JsonResponse(
                    {
                       'success': True,
                       'date': notif.date_created.strftime('%B %d, %Y, %#I:%M %p'),
                       'subject': notif.notif_type.name,
                       'title': notif.record.title,
                       'classification': notif.record.classification.name,
                       'psced': notif.record.psced_classification.name,
                       'recordID': notif.record_id,
                       'status': record_status.status,
                        'subject-body': notif.notif_type.name
                            + ' by '
                            + notif.user.first_name
                            + notif.user.last_name,
                            'checked-by': notif.user.first_name + ' ' + notif.user.last_name,
                            'authors': listOfAuthors(request, notif.record_id),
                        }
                    ) 
                    
                elif notif.notif_type.name == 'Role Request Approved':
                    return JsonResponse({'success': True,
                                        'fname': notif.recipient.first_name,
                                        'mname': notif.recipient.middle_name,
                                        'lname': notif.recipient.last_name,
                                        'username': notif.recipient.username,
                                        'email': notif.recipient.email,
                                        'date': notif.date_created.strftime('%B %d, %Y, %#I:%M %p'),
                                        'subject': notif.notif_type.name,
                                        'request': "Role Request Student",
                                        'subject-body':notif.notif_type.name+' by '+notif.user.first_name+notif.user.last_name,
                                        'approved-by': notif.user.first_name+' '+notif.user.last_name})

class AdviserNotification(View):
    name = 'notifications/adviser_notification_page.html'

    @method_decorator(authorized_roles(roles=['adviser']))
    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(Q(recipient=user.id) | Q(notif_type=NotificationType.objects.get(pk=6)) | Q(notif_type=NotificationType.objects.get(pk=1)) | Q(notif_type=NotificationType.objects.get(pk=2))).order_by('-date_created')
        request.session['notif_count'] = notifications.count()
        return render(request, self.name, notificationDisplay(request, notifications, 'Filter'))
    def post(self, request):
        if request.method == 'POST':
            user = request.user
            # for filter
            if 'all' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) | Q(notif_type=NotificationType.objects.get(pk=6)) | Q(notif_type=NotificationType.objects.get(pk=1)) | Q(notif_type=NotificationType.objects.get(pk=2))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'ALL'))
            elif 'read' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(is_read=True)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Read'))
            elif 'unread' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(is_read=False)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Unread'))
            elif 'rrs' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) | Q(notif_type=NotificationType.objects.get(pk=1))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Student'))
            elif 'rra' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) | Q(notif_type=NotificationType.objects.get(pk=2))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Adviser'))
            elif 'nrpt' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(notif_type=NotificationType.objects.get(pk=3))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Proposal/Thesis'))
            elif 'nrp' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(notif_type=NotificationType.objects.get(pk=4))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Project'))
            elif 'resubmission' in request.POST:
                notifications = Notification.objects.filter(Q(recipient=user.id) & Q(notif_type=NotificationType.objects.get(pk=5))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Resubmissions'))

            if request.POST.get('removeNotification'):
                idList = request.POST.getlist('listOfID[]')
                for id in idList:
                    Notification.objects.get(pk=id).delete()
                return JsonResponse({'success': True})

            if request.POST.get('roleChange'):
                role = request.POST.get('role')
                id = request.POST.get('id')
                User.objects.filter(pk=id).update(role=UserRole.objects.get(name=role))
                removeRequest = RoleRequest.objects.get(user=User.objects.get(pk=id))
                removeRequest.delete()
                roleRequestApproved(request, request.user.id, User.objects.get(pk=id).id)
                return JsonResponse({'success': True})

            # content for each notification -> 2nd box content
            if request.POST.get('displayContent'):
                id = request.POST.get('notifID')
                notifications = Notification.objects.filter(Q(recipient=user.id) | Q(notif_type=NotificationType.objects.get(pk=6)) | Q(notif_type=NotificationType.objects.get(pk=1)) | Q(notif_type=NotificationType.objects.get(pk=2)))
                return notificationContent(request, id, notifications)

class KTTONotification(View):
    name = 'notifications/ktto_notification_page.html'

    @method_decorator(authorized_roles(roles=['ktto']))
    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id)).order_by('-date_created')
        request.session['notif_count'] = notifications.count()
        return render(request, self.name, notificationDisplay(request, notifications, 'Filter'))
    def post(self, request):
        if request.method == 'POST':
            user = request.user
            # for filter
            if 'all' in request.POST:
                notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'ALL'))
            elif 'read' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(is_read=True)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Read'))
            elif 'unread' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(is_read=False)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Unread'))
            elif 'rrs' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=1))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Student'))
            elif 'rra' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=2))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Adviser'))
            elif 'nrpt' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=3))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Proposal/Thesis'))
            elif 'nrp' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=4))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Project'))
            elif 'resubmission' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=5))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Resubmissions'))

            if request.POST.get('removeNotification'):
                idList = request.POST.getlist('listOfID[]')
                for id in idList:
                    Notification.objects.get(pk=id).delete()
                return JsonResponse({'success': True})

            if request.POST.get('roleChange'):
                role = request.POST.get('role')
                id = request.POST.get('id')
                User.objects.filter(pk=id).update(role=UserRole.objects.get(name=role))
                removeRequest = RoleRequest.objects.get(user=User.objects.get(pk=id))
                removeRequest.delete()
                roleRequestApproved(request, request.user.id, User.objects.get(pk=id).id)
                return JsonResponse({'success': True})

            # content for each notification -> 2nd box content
            if request.POST.get('displayContent'):
                id = request.POST.get('notifID')
                notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id))
                return notificationContent(request, id, notifications)

class RDCONotification(View):
    name = 'notifications/rdco_notification_page.html'

    @method_decorator(authorized_roles(roles=['rdco']))
    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(Q(to_rdco=True) | Q(recipient=user.id)).order_by('-date_created')
        request.session['notif_count'] = notifications.count()
        return render(request, self.name, notificationDisplay(request, notifications, 'Filter'))
    def post(self, request):
        if request.method == 'POST':
            user = request.user
            # for filter
            if 'all' in request.POST:
                notifications = Notification.objects.filter(Q(to_rdco=True) | Q(recipient=user.id)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'ALL'))
            elif 'read' in request.POST:
                notifications = Notification.objects.filter((Q(to_rdco=True) | Q(recipient=user.id)) & Q(is_read=True)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Read'))
            elif 'unread' in request.POST:
                notifications = Notification.objects.filter((Q(to_rdco=True) | Q(recipient=user.id)) & Q(is_read=False)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Unread'))
            elif 'rrs' in request.POST:
                notifications = Notification.objects.filter((Q(to_rdco=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=1))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Student'))
            elif 'rra' in request.POST:
                notifications = Notification.objects.filter((Q(to_rdco=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=2))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Adviser'))
            elif 'nrpt' in request.POST:
                notifications = Notification.objects.filter((Q(to_rdco=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=3))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Proposal/Thesis'))
            elif 'nrp' in request.POST:
                notifications = Notification.objects.filter((Q(to_rdco=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=4))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Project'))
            elif 'resubmission' in request.POST:
                notifications = Notification.objects.filter((Q(to_rdco=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=5))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Resubmissions'))

            if request.POST.get('removeNotification'):
                idList = request.POST.getlist('listOfID[]')
                for id in idList:
                    Notification.objects.get(pk=id).delete()
                return JsonResponse({'success': True})

            if request.POST.get('roleChange'):
                role = request.POST.get('role')
                id = request.POST.get('id')
                User.objects.filter(pk=id).update(role=UserRole.objects.get(name=role))
                removeRequest = RoleRequest.objects.get(user=User.objects.get(pk=id))
                removeRequest.delete()
                roleRequestApproved(request, request.user.id, User.objects.get(pk=id).id)
                return JsonResponse({'success': True})

            # content for each notification -> 2nd box content
            if request.POST.get('displayContent'):
                id = request.POST.get('notifID')
                print(id)
                notifications = Notification.objects.filter(Q(to_rdco=True) | Q(recipient=user.id))
                return notificationContent(request, id, notifications)


class TBINotification(View):
    name = 'notifications/ktto_notification_page.html'

    @method_decorator(authorized_roles(roles=['tbi']))
    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id)).order_by('-date_created')
        request.session['notif_count'] = notifications.count()
        return render(request, self.name, notificationDisplay(request, notifications, 'Filter'))
    def post(self, request):
        if request.method == 'POST':
            user = request.user
            # for filter
            if 'all' in request.POST:
                notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'ALL'))
            elif 'read' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(is_read=True)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Read'))
            elif 'unread' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(is_read=False)).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Unread'))
            elif 'rrs' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=1))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Student'))
            elif 'rra' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=2))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Role Request Adviser'))
            elif 'nrpt' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=3))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Proposal/Thesis'))
            elif 'nrp' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=4))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'New Record Project'))
            elif 'resubmission' in request.POST:
                notifications = Notification.objects.filter((Q(to_ktto=True) | Q(recipient=user.id)) & Q(notif_type=NotificationType.objects.get(pk=5))).order_by('-date_created')
                return render(request, self.name, filterHelper(request, notifications, 'Resubmissions'))

            if request.POST.get('removeNotification'):
                idList = request.POST.getlist('listOfID[]')
                for id in idList:
                    Notification.objects.get(pk=id).delete()
                return JsonResponse({'success': True})

            if request.POST.get('roleChange'):
                role = request.POST.get('role')
                id = request.POST.get('id')
                User.objects.filter(pk=id).update(role=UserRole.objects.get(name=role))
                removeRequest = RoleRequest.objects.get(user=User.objects.get(pk=id))
                removeRequest.delete()
                roleRequestApproved(request, request.user.id, User.objects.get(pk=id).id)
                return JsonResponse({'success': True})

            # content for each notification -> 2nd box content
            if request.POST.get('displayContent'):
                id = request.POST.get('notifID')
                notifications = Notification.objects.filter(Q(to_ktto=True) | Q(recipient=user.id))
                return notificationContent(request, id, notifications)

class ITSONotification(View):
    name = 'notifications/index.html'

    @method_decorator(authorized_roles(roles=['itso']))
    @method_decorator(login_required(login_url='/'))
    def get(self, request):
        return render(request, self.name)

# class NotificationsHomeView(View):
#     name = 'notifications/index.html'

#     def get(self, request):
#         user = request.user
#         received_notifications = Notification.objects.filter(recipient=user)
#         context = {
#             'received_notifications': received_notifications,
#         }
#         return render(request, self.name, context)
