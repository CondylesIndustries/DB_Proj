from django import forms
from django.db import connection
from django.core.exceptions import ValidationError

from .queryhelper import selectOne
from .queryhelper import selectAll
from .queryhelper import execute

class patientRegister(forms.Form):
    selection = selectAll('SELECT company_name FROM insurancecompany')
    drop_down = [(row[0], row[0]) for row in selection]
    first_name = forms.CharField(widget=forms.TextInput, min_length=2, max_length=20)
    last_name = forms.CharField(widget=forms.TextInput, min_length=2, max_length=20)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Date of Birth', input_formats=['%Y-%m-%d'])
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '123-456-7890',
        'pattern': r'\d{3}-\d{3}-\d{4}',
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}))
    insurance_name = forms.ChoiceField(choices=drop_down, label="Insurance Company")
    password1 = forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)
    password2 = forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not Match!')


class doctorRegister(forms.Form):
    selection = selectAll('SELECT facility_name FROM medicalfacility')
    drop_down = [(row[0], row[0]) for row in selection]
    affiliate_office_name = forms.ChoiceField(choices=drop_down, label="Medical Facility")
    first_name = forms.CharField(widget=forms.TextInput, min_length=2, max_length=20)
    last_name = forms.CharField(widget=forms.TextInput, min_length=2, max_length=20)
    specialty = forms.CharField(widget=forms.TextInput, min_length=2, max_length=20)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'name@example.com'}))
    password1 = forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)
    password2 = forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not Match!')

class insuranceRegister(forms.Form):
    company_name = forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)
    street =  forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)
    city =  forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)
    state =  forms.CharField(widget=forms.TextInput, min_length=2, max_length=2)
    zip_code = forms.CharField(widget=forms.TextInput, min_length=5, max_length=5)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
            'placeholder': '123-456-7890',
            'pattern': r'\d{3}-\d{3}-\d{4}',
        }))
    password1 = forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)
    password2 = forms.CharField(widget=forms.TextInput, min_length=6, max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not Match!')