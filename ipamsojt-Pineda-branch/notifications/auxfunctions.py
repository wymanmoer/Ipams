from accounts.models import UserRecord
from .models import Notification
from records.models import CheckedRecord, Author
from django.http import HttpResponse, JsonResponse
import datetime


# list of Authors in records
def listOfAuthors(request, recordID):
    authors = []
    # record_authors = UserRecord.objects.filter(record=recordID)
    # for author in record_authors:
    #     authors.append(author.user.first_name+' '+author.user.last_name+', ')
    record_authors = Author.objects.filter(record=recordID)
    for author in record_authors:
        authors.append(author.name + ',')
    return authors


# default display notification content of the first notification upon load of the page
def notificationDisplay(request, notification, category):
    notifications = notification
    for n in notifications:
        print(n.notif_type.name)
    if not notifications:
        context = {
            'category': category,
        }
    else:
        if notifications[0].notif_type.name == 'Role Request Student' or notifications[
            0].notif_type.name == 'Role Request Adviser':
            context = {
                'notifications': notifications,
                'category': category,
                'fname': notifications[0].user.first_name,
                'mname': notifications[0].user.middle_name,
                'lname': notifications[0].user.last_name,
                'username': notifications[0].user.username,
                'email': notifications[0].user.email,
                'course': notifications[0].course,
                'date': notifications[0].date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notifications[0].notif_type.name,
                'id': notifications[0].user.id,
                'role': notifications[0].user.role.name
            }
        elif notifications[0].notif_type.name == 'Role Request Approved':
            if notifications[0].recipient.role.name == 'Student':
                request = "Role Request Student"
            elif notifications[0].recipient.role.name == 'Adviser':
                request = "Role Request Adviser"
            context = {
                'notifications': notifications,
                'category': category,
                'fname': notifications[0].recipient.first_name,
                'mname': notifications[0].recipient.middle_name,
                'lname': notifications[0].recipient.last_name,
                'username': notifications[0].recipient.username,
                'email': notifications[0].recipient.email,
                'date': notifications[0].date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notifications[0].notif_type.name,
                'request': request,
                'subject_body': notifications[0].notif_type.name + ' by ' + notifications[0].user.first_name +
                                notifications[0].user.last_name,
                'approved_by': notifications[0].user.first_name + ' ' + notifications[0].user.last_name,
                'recipient': notifications[0].user.first_name + ' ' + notifications[0].user.last_name
            }
        elif notifications[0].notif_type.name == 'New Record Proposal/Thesis' or notifications[
            0].notif_type.name == 'New Record Project' or notifications[0].notif_type.name == 'Resubmission':
            context = {
                'notifications': notifications,
                'category': category,
                'date': notifications[0].date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notifications[0].notif_type.name,
                'title': notifications[0].record.title,
                'classification': notifications[0].record.classification.name,
                'psced': notifications[0].record.psced_classification.name,
                'recordID': notifications[0].record.id,
                'authors': listOfAuthors(request, notifications[0].record.id)
            }
        elif notifications[0].notif_type.name == 'Request to Delete Record':
            context = {
                'notifications': notifications,
                'category': category,
            }
        elif notifications[0].notif_type.name == 'Approved Request to Delete Record':
            context = {
                'notifications': notifications,
                'category': category,
            }

        elif notifications[0].notif_type.name == 'Request to Download Abstract':
            context = {
                'notifications': notifications,
                'category': category,
            }

        elif notifications[0].notif_type.name == 'Approved Request to Download Abstract':
            record_status = CheckedRecord.objects.filter(record=notifications[0].record.id).latest('status')
            context = {
                'notifications': notifications,
                'category': category,
                'date': notifications[0].date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notifications[0].notif_type.name,
                'title': notifications[0].record.title,
                'classification': notifications[0].record.classification.name,
                'psced': notifications[0].record.psced_classification.name,
                'recordID': notifications[0].record.id,
                'status': record_status.status,
                'authors': listOfAuthors(request, notifications[0].record.id),
                'subject_body': notifications[0].notif_type.name + ' by ' + notifications[0].user.first_name +
                                notifications[0].user.last_name,
                'checked_by': notifications[0].user.first_name + ' ' + notifications[0].user.last_name,
            }

    return context


# filter notifications
def filterHelper(request, notifications, category):
    request.session['notif_count'] = notifications.count()
    return notificationDisplay(request, notifications, category)


def notificationContent(request, id, notifications):
    Notification.objects.filter(pk=id).update(is_read=True)
    request.session['notif_count'] = notifications.count()
    notif = Notification.objects.get(pk=id)
    if notif.notif_type.name == 'Role Request Student' or notif.notif_type.name == 'Role Request Adviser':

        return JsonResponse(
            {
                'success': True,
                'fname': notif.user.first_name,
                'mname': notif.user.middle_name,
                'lname': notif.user.last_name,
                'username': notif.user.username,
                'email': notif.user.email,
                'course': notif.course,
                'date': notif.date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notif.notif_type.name,
                'id': notif.user_id,
                'role': notif.user.role.name,
            }
        )



    elif notif.notif_type.name == 'Role Request Approved':
        if notif.recipient.role.name == 'Student':
            request = "Role Request Student"
        elif notif.recipient.role.name == 'Adviser':
            request = "Role Request Adviser"
        return JsonResponse(
            {
                'success': True,
                'fname': notif.user.first_name,
                'mname': notif.user.middle_name,
                'lname': notif.user.last_name,
                'username': notif.user.username,
                'email': notif.user.email,
                'course': notif.course,
                'date': notif.date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notif.notif_type.name,
                'id': notif.user_id,
                'role': notif.user.role.name,
            }
        )

    elif notif.notif_type.name == 'New Record Proposal/Thesis' or notif.notif_type.name == 'New Record Project' or notif.notif_type.name == 'Resubmission':
        return JsonResponse(
            {
                'success': True,
                'date': notif.date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notif.notif_type.name,
                'title': notif.record.title,
                'classification': notif.record.classification.name,
                'psced': notif.record.psced_classification.name,
                'recordID': notif.record_id,
                'authors': listOfAuthors(request, notif.record_id),
            }
        )
    elif notifications[0].notif_type.name == 'Request to Delete Record':
        return JsonResponse({'success': True})
    elif notifications[0].notif_type.name == 'Approved Request to Delete Record':
        return JsonResponse({'success': True})
    elif notifications[0].notif_type.name == 'Request to Download Abstract':
        return JsonResponse({'success': True,})
    elif notifications[0].notif_type.name == 'Approved Request to Download Abstract':
        return JsonResponse({'success': True})


def notificationDisplayStudent(request, notification, category):
    notifications = notification
    if not notifications:
        context = {
            'category': category,
        }
    else:
        if notifications[0].notif_type.name == 'Record Approved' or notifications[
            0].notif_type.name == 'Record Decline':
            record_status = CheckedRecord.objects.filter(record=notifications[0].record.id).latest('status')
            context = {
                'notifications': notifications,
                'category': category,
                'date': notifications[0].date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notifications[0].notif_type.name,
                'title': notifications[0].record.title,
                'classification': notifications[0].record.classification.name,
                'psced': notifications[0].record.psced_classification.name,
                'recordID': notifications[0].record.id,
                'status': record_status.status,
                'subject_body': notifications[0].notif_type.name + ' by ' + notifications[0].user.first_name +
                                notifications[0].user.last_name,
                'checked_by': notifications[0].user.first_name + ' ' + notifications[0].user.last_name,
                'authors': listOfAuthors(request, notifications[0].record.id)
            }
        elif notifications[0].notif_type.name == 'Role Request Approved':
            context = {
                'notifications': notifications,
                'category': category,
                'fname': notifications[0].recipient.first_name,
                'mname': notifications[0].recipient.middle_name,
                'lname': notifications[0].recipient.last_name,
                'username': notifications[0].recipient.username,
                'email': notifications[0].recipient.email,
                'date': notifications[0].date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notifications[0].notif_type.name,
                'request': "Role Request Student",
                'subject_body': notifications[0].notif_type.name + ' by ' + notifications[0].user.first_name +
                                notifications[0].user.last_name,
                'approved_by': notifications[0].user.first_name + ' ' + notifications[0].user.last_name
            }
        elif notifications[0].notif_type.name == 'Approved Request to Delete Record':
            context = {
                'notifications': notifications,
                'category': category,
            }

        elif notifications[0].notif_type.name == 'Approved Request to Download Abstract':
            record_status = CheckedRecord.objects.filter(record=notifications[0].record.id).latest('status')
            context = {
                'notifications': notifications,
                'category': category,
                'date': notifications[0].date_created.strftime('%B %d, %Y, %#I:%M %p'),
                'subject': notifications[0].notif_type.name,
                'title': notifications[0].record.title,
                'classification': notifications[0].record.classification.name,
                'psced': notifications[0].record.psced_classification.name,
                'recordID': notifications[0].record.id,
                'status': record_status.status,
                'authors': listOfAuthors(request, notifications[0].record.id),
                'subject_body': notifications[0].notif_type.name + ' by ' + notifications[0].user.first_name +
                                notifications[0].user.last_name,
                'checked_by': notifications[0].user.first_name + ' ' + notifications[0].user.last_name,
            }

    return context


def filterHelperStudent(request, notifications, category):
    request.session['notif_count'] = notifications.count()
    return notificationDisplayStudent(request, notifications, category)


