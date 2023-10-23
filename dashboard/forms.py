# from django import forms
# from .models import ExperimentData

# class ExperimentDataForm(forms.ModelForm):
#     experiment_number = forms.ChoiceField(
#         choices=[('exp1', 'Experiment 1'), ('exp2', 'Experiment 2'), ('exp3', 'Experiment 3')])

#     class Meta:
#         model = ExperimentData
#         fields = ['name', 'matrikel_number', 'experiment_number', 'report', 'raw_data']
# class ExperimentSearchForm(forms.Form):
#     experiment_number = forms.ChoiceField(
#         choices=[('', '--- Select ---'), ('exp1', 'Experiment 1'), ('exp2', 'Experiment 2'), ('exp3', 'Experiment 3')],
#         required=False,
#         widget=forms.Select(attrs={'id': 'experiment-dropdown'})
#     )
from django.core.exceptions import ValidationError
from django.forms import DateInput
from django import forms
from .models import ExperimentData, Deadline
from django.forms import ModelChoiceField
import pandas as pd
from io import BytesIO
from .models import Template
from django.db.models import Q

SEMESTER_CHOICES = [
    ('summer_2023', 'Summer 2023'),
    ('fall_2023', 'Fall 2023'),
    ('summer_2024', 'Summer 2024'),
    ('fall_2024', 'Fall 2024'),
]

class UniqueExperimentNamesModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.experiment_name

# class ExperimentDataForm(forms.ModelForm):
#     experiment_number = forms.ModelChoiceField(
#         queryset=Deadline.objects.all().distinct('experiment_name')
#     )

#     class Meta:
#         model = ExperimentData
#         fields = ['name', 'matrikel_number', 'experiment_number', 'report', 'raw_data','semester']
class ExperimentDataForm(forms.ModelForm):
    experiment_number = forms.ModelChoiceField(
        queryset=Deadline.objects.all().distinct('experiment_name')
    )

    def clean_report(self):
        file = self.cleaned_data.get('report')
        if not file.name.endswith('.pdf'):
            raise ValidationError('File must be a PDF.')
        return file

    def clean_raw_data(self):
        file = self.cleaned_data.get('raw_data')
        experiment_name = self.cleaned_data.get('experiment_number')  # Retrieve experiment name/number from form data

        if not (file.name.endswith('.xlsx') or file.name.endswith('.xls')):
            raise ValidationError('File must be in Excel format (.xlsx or .xls).')

        # Check if there's a template for the given experiment
        try:
            template_instance = Template.objects.get(experiment_name=experiment_name)
            template_file = template_instance.template
            template_xls = pd.ExcelFile(template_file.path)
        except Template.DoesNotExist:
            template_xls = None

        xls = pd.ExcelFile(BytesIO(file.read()))
        file.seek(0)  # Reset file position to the beginning

        # If a template exists, check that the raw data matches the template
        if template_xls:
            # Check if sheet names match
            if set(xls.sheet_names) != set(template_xls.sheet_names):
                raise ValidationError("Sheet names do not match the template.")
                
            # Check if columns in each sheet match
            for sheet_name in xls.sheet_names:
                raw_df = pd.read_excel(BytesIO(file.read()), sheet_name=sheet_name)
                file.seek(0)  # Reset file position to the beginning
                template_df = pd.read_excel(template_xls, sheet_name=sheet_name)
                
                if set(raw_df.columns) != set(template_df.columns):
                    raise ValidationError(f"The columns in sheet '{sheet_name}' do not match the template.")

        return file

    class Meta:
        model = ExperimentData
        fields = ['name', 'matrikel_number', 'experiment_number', 'report', 'raw_data', 'semester']

# class ExperimentSearchForm(forms.Form):
#     experiment_number = forms.ModelChoiceField(
#         queryset=Deadline.objects.all(),
#         required=False,
#         widget=forms.Select(attrs={'id': 'experiment-dropdown'})
#     )
class ExperimentSearchForm(forms.Form):
    experiment_number = forms.ChoiceField(choices=[], required=False)
    matrikel_number = forms.IntegerField(required=False)
    semester = forms.ChoiceField(choices=[('', 'Select Semester')] + list(SEMESTER_CHOICES), required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['experiment_number'].choices = [('', 'Select Experiment Number')] + [(x, x) for x in unique_experiment_numbers()]

def unique_experiment_numbers():
    return ExperimentData.objects.values_list('experiment_number', flat=True).distinct()

class DeadlineForm(forms.ModelForm):
    experiment_deadline = forms.DateField(
        widget=DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Deadline
        fields = ['experiment_name', 'experiment_deadline', 'matrikel_number', 'semester']

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['experiment_name', 'template']

    def clean_template(self):
        uploaded_file = self.cleaned_data.get('template')
        if not (str(uploaded_file).endswith('.xls') or str(uploaded_file).endswith('.xlsx')):
            raise forms.ValidationError("Invalid file type: Please upload an Excel file (.xls or .xlsx)")
        return uploaded_file

