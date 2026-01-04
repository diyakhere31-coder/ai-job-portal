from django import forms
from django.forms import ModelForm
from jobapp.models import ItJobs, MechJobs, CivilJobs
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from jobapp.models import JobApplication


# Use your custom user model dynamically
CustomUser = get_user_model()


# -------------------------------------------------------------------
# IT Jobs Forms
class CreateItJobsForm(ModelForm):
    class Meta:
        model = ItJobs
        exclude = ['recruiter']
        widgets = {
            "job_title": forms.TextInput(attrs={
                "placeholder": "software developer / Software Engineer"
            }),
            "company_name": forms.TextInput(attrs={
                "placeholder": "ABC Technical Pvt Ltd"
            }),
            "job_location": forms.TextInput(attrs={
                "placeholder": "Factory / Site Location"
            }),
        }


class UpdateItJobsForm(ModelForm):
    class Meta:
        model = ItJobs
        fields = '__all__'

# -------------------------------------------------------------------
# Mechanical Jobs Forms
class CreateMechanicalJobForm(ModelForm):
    class Meta:
        model = MechJobs
        exclude = ['recruiter']
        widgets = {
            "job_title": forms.TextInput(attrs={
                "placeholder": "Mechanical Engineer / Maintenance Engineer"
            }),
            "company_name": forms.TextInput(attrs={
                "placeholder": "ABC Mechanical Pvt Ltd"
            }),
            "job_location": forms.TextInput(attrs={
                "placeholder": "Factory / Site Location"
            }),
        }
class UpdateMechanicalJobsForm(ModelForm):
    class Meta:
        model = MechJobs
        fields = '__all__'

# -------------------------------------------------------------------
# Civil Jobs Forms
class CreateCivilJobsForm(ModelForm):
    class Meta:
        model = CivilJobs
        exclude = ['recruiter']
        widgets = {
            "job_title": forms.TextInput(attrs={
                "placeholder": "Civil Engineer"
            }),
            "company_name": forms.TextInput(attrs={
                "placeholder": "ABC Civil Pvt Ltd"
            }),
            "job_location": forms.TextInput(attrs={
                "placeholder": "Factory / Site Location"
            }),
        }
class UpdateCivilJobsForm(ModelForm):
    class Meta:
        model = CivilJobs
        fields = '__all__'


# -------------------------------------------------------------------
# -------------------------------------------------------------------
# Admin Registration Form
class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = True
        user.is_user = False
        user.is_recruiter = False
        if commit:
            user.save()
        return user


# -------------------------------------------------------------------
# User Registration Form
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_admin = False
        user.is_user = True
        user.is_recruiter = False
        if commit:
            user.save()
        return user

# -------------------------------------------------------------------
# Recruiter Job Post Form
from jobapp.models import JobPost

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        exclude = ['recruiter', 'posted_on']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# -------------------------------------------------------------------
# Job Application Form (Resume Upload + Candidate Details)

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            'name',
            'email',
            'contact',
            'qualification',
            'resume'
        ]

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
        }
