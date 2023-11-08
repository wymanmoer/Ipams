from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import File, Folder, Subfolder, LoginEvent, RecordAccessEvent, DeletedFileEvent, UploadCount, FileRenameEvent, StudentFolder, DownloadEvent
from .forms import FileUploadForm, FolderCreateForm, UploadRecordForm
from django.http import JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from accounts.models import User
from records.models import Classification, Record, RecordFile, PSCEDClassification, RecordDownloadRequest, CheckedRecord
from django.utils import timezone
from datetime import date
from django.db.models import Sum
from django.contrib.auth import get_user_model
import json, os, mimetypes
from django.http import HttpResponseBadRequest
from django.http import Http404
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from .helpers import count_currently_logged_in_users
from django.utils.text import slugify
from django.db.models import Q
import zipfile, errno
from django.views.decorators.http import require_POST
def home_view(request):
    # Fetch the records with access counts
    records = Record.objects.all()

    # Calculate the total access count
    total_access_count = records.aggregate(total_access_count=Sum('access_count'))['total_access_count'] or 0

    # Calculate the number of currently logged-in users
    currently_logged_in_users_count = count_currently_logged_in_users()

    # Count marked requests where is_marked is equal to 1
    marked_requests_count = RecordDownloadRequest.objects.filter(is_marked=1).count()

    # Count marked requests where is_marked is equal to 0
    unmarked_requests_count = RecordDownloadRequest.objects.filter(is_marked=0).count()

    # Count the approved records checked by user with ID 4
    approved_records_count = CheckedRecord.objects.filter(status='approved', checked_by_id=4).count()

    unapproved_records_count = CheckedRecord.objects.filter(status='declined', checked_by_id=4).count()

    total_delete_count = DeletedFileEvent.objects.count()

    # Calculate the total upload count
    total_upload_count = RecordFile.objects.count()

    # Count the number of renamed files
    renamed_files_count = FileRenameEvent.objects.count()

    # Count the number of downloaded files
    total_download_count = DownloadEvent.objects.count()

    context = {
        'total_access_count': total_access_count,
        'total_download_count': total_download_count,  # Add the download count here
        'currently_logged_in_users_count': currently_logged_in_users_count,
        'marked_requests_count': marked_requests_count,
        'unmarked_requests_count': unmarked_requests_count,
        'approved_records_count': approved_records_count,
        'unapproved_records_count': unapproved_records_count,
        'total_delete_count': total_delete_count,
        'total_upload_count': total_upload_count,
        'renamed_files_count': renamed_files_count,
    }

    return render(request, 'home.html', context)


def browse_files_view(request):
    # Implement your home view logic here
    return render(request, 'browse_files.html')


# def ipams_files_view(request):
#     return render(request, 'ipams_files.html')


def personal_files_view(request):
    # Get the list of folders associated with the current user
    folders = StudentFolder.objects.filter(user=request.user)

    context = {
        'folders': folders,
    }

    # Implement your view for personal files here
    return render(request, 'personal_files.html', context)


@login_required
def ipams_files_view(request):
    uploaded_files = File.objects.all()
    folders = Folder.objects.all()
    error_messages = []  # List to store error messages for invalid file types

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = request.FILES.getlist('file_field')
            folder_id = request.POST.get('folder_id')

            if folder_id:
                folder = get_object_or_404(Folder, id=folder_id)
            else:
                folder = None

            allowed_extensions = ['.pdf', '.docx', '.zip', '.jpg']

            for file in files:
                # Check if the file extension is allowed
                file_extension = os.path.splitext(file.name)[1].lower()
                if file_extension not in allowed_extensions:
                    error_messages.append(f"Invalid file type for {file.name}. Only PDF, DOCX, ZIP, and JPG are allowed.")
                    continue  # Skip processing this file

                # Create a new file and associate it with the selected folder (or None)
                new_file = File(file=file, name=file.name, folder=folder)
                new_file.username = request.user.username
                new_file.save()

            uploaded_files = File.objects.all()
    else:
        form = FileUploadForm()  # Create a new form instance if it's a GET request

    return render(request, 'ipams_files.html', {'uploaded_files': uploaded_files, 'folders': folders, 'error_messages': error_messages, 'form': form})


# Create Folder View
def create_folder_view(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        parent_folder_id = request.POST.get('parent_folder_id')

        # Create a new folder with the provided name and parent_folder
        if parent_folder_id:
            parent_folder = get_object_or_404(Folder, id=parent_folder_id)
            new_folder = Folder(name=folder_name, parent_folder=parent_folder)
        else:
            new_folder = Folder(name=folder_name)

        new_folder.save()
        # Redirect to a different page after folder creation
        return redirect('ipams_files_view')  # Replace 'success_page' with the actual URL name
    else:
        return render(request, 'ipams_files.html')  # Render a form for creating folders


# Move Folder View
def move_folder_view(request, folder_id):
    if request.method == 'POST':
        new_parent_folder_id = request.POST.get('new_parent_folder_id')
        folder = get_object_or_404(Folder, id=folder_id)

        if new_parent_folder_id:
            new_parent_folder = get_object_or_404(Folder, id=new_parent_folder_id)
            folder.parent_folder = new_parent_folder
        else:
            folder.parent_folder = None

        folder.save()
        return JsonResponse({'message': 'Folder moved successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


# Delete Folder View
def delete_folder_view(request, folder_id):
    if request.method == 'POST':
        folder = get_object_or_404(Folder, id=folder_id)

        # Delete the folder and its contents (files and subfolders)
        folder.delete()
        return JsonResponse({'message': 'Folder deleted successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


def rename_file(request, record_id):
    if request.method == 'POST':
        new_file_name = request.POST.get('new_file_name')
        record_instance = get_object_or_404(Record, pk=record_id)

        # Perform validation and security checks as needed

        # Store the old file name before renaming
        old_file_name = record_instance.title

        # Update the file name
        record_instance.title = new_file_name
        record_instance.save()

        # Create a FileRenameEvent instance to track the renaming event
        file_rename_event = FileRenameEvent(
            user=request.user,
            record=record_instance,
            old_file_name=old_file_name,
            new_file_name=new_file_name
        )
        file_rename_event.save()

        messages.success(request, 'File name updated successfully')
        return redirect('record_detail', record_id=record_id)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
@login_required
def edit_profile(request, user_id):
    # Ensure that the user can only edit their own profile
    if request.user.id != user_id:
        return JsonResponse({'success': False, 'error': 'Unauthorized'})

    if request.method == 'POST':
        # Get the user object
        user = User.objects.get(id=user_id)

        # Retrieve the form data
        new_username = request.POST.get('new_username')
        new_email = request.POST.get('new_email')
        new_password = request.POST.get('new_password')

        # Update the user's profile information
        user.username = new_username
        user.email = new_email

        # Check if a new password is provided and update it
        if new_password:
            user.set_password(new_password)

        user.save()

        # You can also return a success response here
        return JsonResponse({'success': True})
    else:
        # Render the edit profile form page with the user's current data
        user = User.objects.get(id=user_id)
        return render(request, 'edit_profile.html', {'user': user})

def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('currentPassword')
        new_password = request.POST.get('newPassword')

        # Perform password change logic here (you may need to use Django's password validation)
        user = request.user  # Assuming you have a user object
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True})

    return JsonResponse({'success': False})

def file_info(request,pk):

    file =File.objects.get(id=pk)
    return render(request, 'file_info.html', {'File':file})

def download_file(request, file_id):
    record_file = get_object_or_404(RecordFile, id=file_id)

    # Check if the file exists
    if record_file.file:
        response = HttpResponse(record_file.file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{record_file.file.name}"'
        return response
    else:
        # Return a 404 response if the file doesn't exist
        raise Http404("File not found")

def all_folders(request, folder_id):
    try:
        folder = Folder.objects.get(pk=folder_id)
    except Folder.DoesNotExist:
        # Handle the case where the folder does not exist
        return render(request, 'folder_not_found.html')

    # Assuming you want to retrieve files within this folder
    files_in_folder = folder.file_set.all()

    # Get the associated classification for the folder
    classification = folder.classification

    try:
        subfolders = Subfolder.objects.filter(parent_folder_id=folder_id)
    except Subfolder.DoesNotExist:
        subfolders = []

    context = {
        'folder_id': folder_id,
        'folder_name': folder.name,
        'classification_id': classification.id,
        'classification_name': classification.name,
        'files_in_folder': files_in_folder,  # Pass the files in the folder
        'subfolders': subfolders,  # Pass the subfolders
    }

    return render(request, 'all_folders.html', context)





def classification_list(request):
    # Retrieve all Classification objects from the database
    classifications = Classification.objects.all()
    psedclassifications = PSEDClassification.objects.all()

    # Pass the data to the template
    context = {'classifications': classifications,
               'psedclassifications': psedclassifications}

    return render(request, 'all_folders.html', context)

def subfolders(request, subfolder_id):
    try:
        subfolders = Subfolder.objects.filter(parent_folder_id=subfolder_id)
    except Subfolder.DoesNotExist:
        subfolders = []

    try:
        parent_subfolder = Subfolder.objects.get(id=subfolder_id)
    except Subfolder.DoesNotExist:
        parent_subfolder = None

    records = []

    if parent_subfolder:
        # Access the associated classification of the parent_subfolder
        classification_id = parent_subfolder.parent_folder_id

        if classification_id:
            # If a classification_id is associated with the parent_subfolder, filter records based on it
            records = Record.objects.filter(psced_classification=parent_subfolder.pscedclassification, classification_id=classification_id)

    context = {
        'subfolders': subfolders,
        'parent_subfolder': parent_subfolder,
        'records': records,
    }

    return render(request, 'all_subfolders.html', context)


def records_table(request):
    # Fetch the records with access counts
    records = Record.objects.all()

    # Calculate the total access count
    total_access_count = records.aggregate(total_access_count=Sum('access_count'))['total_access_count'] or 0

    context = {
        'records': records,  # Pass the records to the template
        'total_access_count': total_access_count,
    }

    return render(request, 'all_records.html', context)


@login_required
def record_detail(request, record_id):
    record = get_object_or_404(Record, id=record_id)

    if request.method == 'POST':
        form = UploadRecordForm(request.POST, request.FILES)
        if form.is_valid():
            for file in request.FILES.getlist('file'):
                record_file = RecordFile(record=record, file=file, user=request.user, record_file_name=file.name)
                record_file.save()

                # Update the upload count in the UploadCount model
                upload_count, created = UploadCount.objects.get_or_create(user=request.user, record=record)
                upload_count.count += 1
                upload_count.save()

            # You can add any additional processing here

    else:
        form = UploadRecordForm()

    return render(request, 'record_detail.html', {'record': record, 'form': form})

def increment_access_count(request, record_id):
    record = get_object_or_404(Record, pk=record_id)

    # Increment the access count
    record.access_count += 1
    record.save()

    # Calculate the total access count
    total_access_count = Record.objects.aggregate(total_access_count=models.Sum('access_count'))['total_access_count'] or 0

    # Print the value to the console
    print("Total Access Count:", total_access_count)

    # Prepare the data to send back as JSON, including the total access count
    data = {
        'success': True,
        'access_count': record.access_count,
        'total_access_count': total_access_count,
        'record_detail_url': reverse('record_detail', args=[record.id])  # Replace 'record_detail' with your view name
    }

    return JsonResponse(data)

def psced_chart_view(request):
    # Get all PSCEDClassification objects
    psced_classifications = PSCEDClassification.objects.all()

    # Create lists to store PSCEDClassification names and their corresponding record counts
    psced_classification_names = []
    record_counts = []

    # Iterate through each PSCEDClassification
    for psced_classification in psced_classifications:
        psced_classification_names.append(psced_classification.name)
        # Count the number of records with this PSCEDClassification
        record_count = Record.objects.filter(psced_classification=psced_classification).count()
        record_counts.append(record_count)

    # Prepare data for the chart
    data = {
        'labels': psced_classification_names,
        'data': record_counts,
    }

    return JsonResponse(data)

def chart_view(request):
    # Get all Classification objects
    classifications = Classification.objects.all()

    # Create lists to store classification names and their corresponding record counts
    classification_names = []
    record_counts = []

    # Iterate through each classification
    for classification in classifications:
        classification_names.append(classification.name)
        # Count the number of records with this classification
        record_count = Record.objects.filter(classification=classification).count()
        record_counts.append(record_count)

    # Prepare data for the chart
    data = {
        'labels': classification_names,
        'data': record_counts,
    }

    return JsonResponse(data)

from django.shortcuts import render
from .models import LoginEvent
@login_required
def audit_logs(request, category=None):
    # Retrieve the latest 10 login events (order by login_time in descending order)
    login_events_with_logout = LoginEvent.objects.filter(log_out_time__isnull=False).order_by('-login_time')[:10]

    login_events_without_logout = LoginEvent.objects.filter(log_out_time__isnull=True).order_by('-login_time')[:10]

    # Retrieve the latest 10 record access events (order by access_time in descending order)
    record_access_events = RecordAccessEvent.objects.all().order_by('-access_time')[:10]

    # Retrieve the latest 10 delete events (order by access_time in descending order)
    delete_events = DeletedFileEvent.objects.all().order_by('-delete_time')[:10]

    # Retrieve the latest 10 upload events (order by upload_time in descending order)
    upload_events = RecordFile.objects.filter(user=request.user).order_by('-created_at')[:10]

    # Retrieve the latest 10 rename events (order by rename_time in descending order)
    rename_events = FileRenameEvent.objects.all().order_by('-rename_time')[:10]

    download_events = DownloadEvent.objects.all().order_by('downloaded_date')[:10]

    # Combine and sort all types of events by timestamp in descending order
    events = sorted(
        list(login_events_with_logout) + list(login_events_without_logout) + list(record_access_events) +
        list(delete_events) + list(upload_events) + list(rename_events) + list(download_events),  # Add rename_events
        key=lambda event: (
            event.login_time if hasattr(event, 'login_time') else
            (event.delete_time if hasattr(event, 'delete_time') else
            (event.access_time if hasattr(event, 'access_time') else
            (event.downloaded_date if hasattr(event, 'downloaded_date') else
            (event.rename_time if hasattr(event, 'rename_time') else event.created_at))))
        ),
        reverse=True
    )[:15]

    if category:
        # Filter events by category if specified
        events = [event for event in events if get_category(event) == category]

    context = {
        'events': events,
    }

    return render(request, 'audit.html', context)

def get_category(event):
    # A function to determine the category of an event
    if hasattr(event, 'login_time'):
        return 'login'
    elif hasattr(event, 'delete_time'):
        return 'delete'
    elif hasattr(event, 'created_at'):
        return 'upload'
    elif hasattr(event, 'rename_time'):
        return 'rename'
    elif hasattr(event, 'access_time'):
        return 'record'
    else:
        return 'unknown'



def download_all_files(request, record_id):
    record = get_object_or_404(Record, id=record_id)
    files = record.files.all()

    # Create a zip archive containing all files
    zip_filename = f"{slugify(record.title)}_files.zip"
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'

    with zipfile.ZipFile(response, 'w') as zipf:
        for file in files:
            zipf.write(file.file.path, file.file.name)

    return response

def log_record_access(request, record_id):
    # Assuming you have a Record model, fetch the corresponding record
    try:
        record = Record.objects.get(id=record_id)
    except Record.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Record not found'})

    # Log the record access event
    RecordAccessEvent.objects.create(user=request.user, record=record)

    return JsonResponse({'success': True})


def download_abstract_file(request, record_id):
    record = get_object_or_404(Record, id=record_id)

    response = FileResponse(record.abstract_file)
    response['Content-Disposition'] = f'attachment; filename="{record.abstract_filename}"'

    # Create a DownloadEvent to log the download
    DownloadEvent.objects.create(
        user=request.user,
        record=record,
        downloaded_file_name=record.abstract_filename,
    )

    return response

def download_record_file(request, record_file_id):
    record_file = get_object_or_404(RecordFile, pk=record_file_id)

    try:
        if record_file.file:
            # Create a DownloadEvent to log the download
            DownloadEvent.objects.create(
                user=request.user,
                record=record_file.record,
                downloaded_file_name=record_file.record_file_name,
            )

            response = FileResponse(record_file.file, as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{record_file.file.name}"'
            return response
    except (ConnectionError, OSError) as e:
        if isinstance(e, OSError) and e.errno == errno.EPIPE:
            # Handle Broken Pipe error (Client closed the connection)
            pass
        else:
            # Handle other exceptions if necessary
            # Log the exception for debugging purposes
            # You may want to return a custom error response here
            return HttpResponse("Error occurred while processing the request")

    raise Http404("File not found")


@login_required  # This decorator ensures that the user is authenticated
def count_deleted_fle(request, recordID, fileID):
    # Get the Record associated with the recordID
    record = get_object_or_404(Record, id=recordID)

    # Find or create a DeletedFileEvent instance associated with the user and the record
    deleted_file_event, created = DeletedFileEvent.objects.get_or_create(user=request.user, record=record)

    # Increment the delete count
    deleted_file_event.delete_count += 1
    deleted_file_event.save()

    # Return a JSON response indicating success
    return JsonResponse({'success': True})



def delete_record_file(request, record_id, file_id):
    if request.method == 'POST':
        try:
            record_file = RecordFile.objects.get(id=file_id, record_id=record_id)
            file_name = record_file.record_file_name  # Get the file name from the record_file_name field
            record_file.delete()

            # Create a DeletedFileEvent instance
            deleted_file_event = DeletedFileEvent(user=request.user, record=record_file.record,
                                                  delete_file_name=file_name)
            deleted_file_event.save()

            return JsonResponse({'success': True})
        except RecordFile.DoesNotExist:
            return JsonResponse({'success': False}, status=404)
    return JsonResponse({'success': False}, status=400)


def record_detail_view(request, record_id, file_id):
    # Retrieve the record
    record = Record.objects.get(id=record_id)

    # Retrieve the file_id (replace this with your logic)
    file_id = RecordFile.objects.get(id=file_id)  # Logic to get the file_id

    context = {
        'record': record,
        'file_id': file_id,
    }

    return render(request, 'record_detail.html', context)


def logout_view(request):
    # Ensure the user is logged in
    if request.user.is_authenticated:
        # Find the latest login event for the user without a logout time
        login_event = LoginEvent.objects.filter(user=request.user, log_out_time__isnull=True).first()
        if login_event:
            login_event.log_out_time = timezone.now()
            login_event.save()

    # Log the user out
    logout(request)

    # Redirect to a different page after logout (e.g., home)
    return redirect('home_view')  # Replace 'home' with the URL name of your home page


@csrf_exempt
def delete_file(request, record_id, file_id):
    if request.method == 'POST':
        try:
            record_file = RecordFile.objects.get(id=file_id, record_id=record_id)
            file_name = record_file.file_name  # Get the file name from the record_file_name field
            record_file.delete()

            # Create a DeletedFileEvent instance
            deleted_file_event = DeletedFileEvent(user=request.user, record=record_file.record, delete_file_name=file_name)
            deleted_file_event.save()

            return JsonResponse({'success': True})
        except RecordFile.DoesNotExist:
            return JsonResponse({'success': False}, status=404)
    return JsonResponse({'success': False}, status=400)


#---------------------------------------------------------------------------------------------------
#Personal Files (Student)

def add_personal_folder(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        if folder_name:
            user = User.objects.get(username=request.user)  # Get the current user
            # Create a new StudentFolder instance and save it to the database
            new_folder = StudentFolder(name=folder_name, user=user)
            new_folder.save()
            return redirect('personal_files_student')  # Redirect to a view that displays the list of folders

    return HttpResponse("Invalid form submission or folder name is missing.")

def student_folders(request, folder_id):
    try:
        folder = StudentFolder.objects.get(id=folder_id)
        record = folder.record  # Access the associated record
    except StudentFolder.DoesNotExist:
        folder = None
        record = None

    context = {
        'folder_id': folder_id,
        'folder': folder,
        'record': record,
    }

    return render(request, 'student_folder.html', context)
def get_events_by_category(request, category):
    if category == 'all':
        events = combine_events(category)
    elif category == 'login':
        events = LoginEvent.objects.all().order_by('-login_time')
    elif category == 'logout':
        events = LoginEvent.objects.filter(log_out_time__isnull=False).order_by('-login_time')
    elif category == 'delete':
        events = DeletedFileEvent.objects.all().order_by('-delete_time')
    elif category == 'upload':
        events = RecordFile.objects.all().order_by('-created_at')
    elif category == 'rename':
        events = FileRenameEvent.objects.all().order_by('-rename_time')
    elif category == 'access':
        events = RecordAccessEvent.objects.all().order_by('-access_time')
    elif category == 'download':
        events = DownloadEvent.objects.all().order_by('-downloaded_date')
    else:
        events = []

    return render(request, 'audit.html', {'events': events})


def personal_files_student(request):
    # Get the list of folders associated with the current user
    folders = StudentFolder.objects.filter(user=request.user)

    context = {
        'folders': folders,
    }


    return render(request, 'personal_files_student.html', context)

def browse_file_student(request):
    # Implement any necessary logic here

    # Redirect to the 'browse_file_student' view
    return render(request, 'browse_file_student.html')

@login_required
def student_records(request, record_id):
    # Check if the request method is POST
    if request.method == 'POST':
        # Get the record object to be approved
        record = Record.objects.get(pk=record_id)

        # Process the form to approve or decline the record
        form = RecordApprovalForm(request.POST, instance=record)
        if form.is_valid():
            # If the record is approved by RDCO
            if form.cleaned_data['status'] == 'approved':
                # Create a folder associated with the approved record
                folder = RecordsFolder(
                    name=record.title,  # Use a meaningful name for the folder
                    description=record.description,
                    record=record,  # Link the folder to the record
                    user=record.user,  # Associate the user
                    role=record.user.role  # Associate the role, if applicable
                )
                folder.save()
                # Optionally, add logic to set other folder properties
                # ...

                # You might want to add additional checks and validation here
                # ...

                # Redirect to a success page or wherever needed
                messages.success(request, 'Record has been approved, and a folder has been created.')
                return redirect('success_url_name')  # Redirect to a success page

    # If it's a GET request or if the form is not valid, render a response
    return render(request, 'your_template.html', {'form': form, 'record': record})

def approved_records_view(request):
    # Query the CheckedRecord model to get approved records with checked_by_id = 4
    approved_records = CheckedRecord.objects.filter(status='approved', checked_by_id=4)

    context = {
        'approved_records': approved_records,
    }

    return render(request, 'approved_records.html', context)

def unapproved_records_view(request):
    # Query the CheckedRecord model to get approved records with checked_by_id = 4
    unapproved_records = CheckedRecord.objects.filter(status='declined', checked_by_id=4)

    context = {
        'unapproved_records': unapproved_records,
    }

    return render(request, 'declined_records.html', context)

def currently_login(request):

    login_events_with_logout = LoginEvent.objects.filter(log_out_time__isnull=True).order_by('-login_time')[:10]

    context = {
        'login_events_with_logout': login_events_with_logout,
    }

    return render(request, 'currently_login.html', context)


def student_all_records(request):
    current_user_full_name = f'{request.user.first_name} {request.user.last_name}'
    records = Record.objects.filter(representative=current_user_full_name)



    context = {
        'records': records,  # Pass the records to the template
    }

    return render(request, 'student_all_records.html', context)
