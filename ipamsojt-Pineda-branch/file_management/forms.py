from django import forms
from .models import File, Folder, StudentFolder
from records.models import RecordFile

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

class FolderCreateForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']


class UploadRecordForm(forms.ModelForm):
    class Meta:
        model = RecordFile
        fields = ['file']

class FolderForm(forms.ModelForm):
    class Meta:
        model = StudentFolder
        fields = ['name']  # Define the fields you want in the form

    def __init__(self, *args, **kwargs):
        super(FolderForm, self).__init__(*args, **kwargs)
        # Add custom attributes or widgets if needed, e.g., to add classes or input types
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Folder Name'})
