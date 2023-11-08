from io import BytesIO

from django import forms
from django.core.files import File
from crispy_forms.helper import FormHelper
from django.forms import ClearableFileInput, FileInput

from records.models import Record, Publication, Conference, Author, Collaboration, Budget, AuthorRole, PublicationLevel, \
    Classification, PSCEDClassification, CheckedRecord, RecordUpload
from datetime import date


ASSESSMENT_CHOICES = (('pending', 'pending'), ('approved', 'approved'), ('declined', 'declined'))

class RecordForm(forms.ModelForm):
    use_required_attribute = False
    year_accomplished = forms.ChoiceField(choices=[("","------------")] + [(str(year), str(year)) for year in range(date.today().year, 1950,-1)], widget=forms.Select(attrs={'class': 'year-field'}))
    year_completed = forms.ChoiceField(choices=[("","------------")] + [("","Not yet completed")] + [(str(year), str(year)) for year in range(date.today().year, 1949, -1)], widget=forms.Select(attrs={'class': 'year-field'}),required=False)


    def __init__(self, *args, **kwargs):
        super(RecordForm, self).__init__(*args, **kwargs)
        self.fields['year_accomplished'].label = 'Year Started'
        self.fields['abstract_file'].label = 'Whole Proposal/Research Paper'

    class Meta:
        model = Record
        fields = ('title', 'year_accomplished', 'year_completed', 'abstract', 'classification', 'psced_classification', 'abstract_file', 'record_type')

    def save(self, commit=True):
        title = self.cleaned_data.get('title')
        year_accomplished = self.cleaned_data.get('year_accomplished')
        year_completed = self.cleaned_data.get('year_completed')
        classification = self.cleaned_data.get('classification')
        psced_classification = self.cleaned_data.get('psced_classification')
        abstract = self.cleaned_data.get('abstract',None)
        # record_len = len(Record.objects.filter(title=title, year_accomplished=year_accomplished, year_completed=year_completed, abstract=abstract,
        #                                        classification=classification,
        #                                        psced_classification=psced_classification))

        # record exist
        record_len = Record.objects.filter(
            title=title,
            year_accomplished=year_accomplished,
            year_completed=year_completed,
            abstract=abstract,
            classification=classification,
            psced_classification=psced_classification,
        ).count()



        if record_len == 0 or abstract is not None:
            # test encryption
            abstract_file = self.cleaned_data.get('abstract_file')
            if abstract_file is not None:
                data = abstract_file.read()
                data = bytearray(data)
                for index, value in enumerate(data):
                    data[index] = value ^ 123
                out = BytesIO()
                out.write(data)
                self.cleaned_data['abstract_file'] = File(out)
                out.close()
                # end test of encryption
            m = super(RecordForm, self).save(commit=False)
            if commit:
                m.save()
            return m
        return None

class PublicationForm(forms.ModelForm):
    use_required_attribute = False
    publication_name = forms.CharField(required=False)

    class Meta:
        model = Publication
        fields = ('isbn', 'issn', 'isi', 'year_published', 'publication_level')

    def save(self, commit=True):
            m = super(PublicationForm, self).save(commit=False)
            m.name = self.cleaned_data.get('publication_name')
            if commit:
                m.save()
            return m

class AuthorForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Author
        fields = ('name', 'author_role')


class BudgetForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Budget
        fields = ('budget_allocation', 'funding_source', 'budget_type')


class ConferenceForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Conference
        fields = ('title', 'date', 'venue', 'conference_level')


class CollaborationForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = Collaboration
        fields = ('industry', 'institution', 'collaboration_type')


class CheckedRecordForm(forms.ModelForm):
    use_required_attribute = False

    class Meta:
        model = CheckedRecord
        fields = ('comment',)
        labels = {
            'comment': 'Comments or Recommendations:',
        }

        label_attrs = {
            'comment': {'style': 'color: black; font-weight: bold;'},
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['comment'].widget.attrs['style'] = 'width: 1000px;'
        self.fields['comment'].widget.attrs['id'] = 'field-comment'
        self.helper.form_class = 'label'


class AssessmentForm(forms.Form):
    comment = forms.CharField(required=False, label='COMMENTS / RECOMMENDATIONS', widget=forms.Textarea(attrs={'cols': 100, 'rows': 20}))


class EditRecordForm(forms.ModelForm):
    use_required_attribute = False
    year_accomplished = forms.ChoiceField(choices=[("","------------")] + [(str(year), str(year)) for year in range(date.today().year, 1950,-1)], widget=forms.Select(attrs={'class': 'year-field'}))
    year_completed = forms.ChoiceField(choices=[("","------------")] + [("","Not yet completed")] + [(str(year), str(year)) for year in range(date.today().year, 1949, -1)], widget=forms.Select(attrs={'class': 'year-field'}),required=False)
    abstract_file = forms.FileField(widget=FileInput)
    def __init__(self, *args, **kwargs):
        super(EditRecordForm, self).__init__(*args, **kwargs)
        self.fields['abstract_file'].required = False
        self.fields['year_accomplished'].label = 'Year Started'
        self.fields['abstract_file'].label = ''

    class Meta:
        model = Record
        fields = ('title', 'year_accomplished', 'year_completed', 'abstract', 'classification', 'psced_classification', 'abstract_file', 'record_type')
    def save(self, commit=True):
        title = self.cleaned_data.get('title')
        year_accomplished = self.cleaned_data.get('year_accomplished')
        year_completed = self.cleaned_data.get('year_completed')
        classification = self.cleaned_data.get('classification')
        psced_classification = self.cleaned_data.get('psced_classification')
        abstract = self.cleaned_data.get('abstract', None)
        # record_len = len(Record.objects.filter(title=title, year_accomplished=year_accomplished, year_completed=year_completed, abstract=abstract,
        #                                        classification=classification,
        #                                        psced_classification=psced_classification))
        record_len = Record.objects.filter(
            title=title,
            year_accomplished=year_accomplished,
            year_completed=year_completed,
            abstract=abstract,
            classification=classification,
            psced_classification=psced_classification,
        ).count()
        
        if record_len == 0 or abstract is not None:
            m = super(EditRecordForm, self).save(commit=False)
            if commit:
                m.save()
            return m
        return None
