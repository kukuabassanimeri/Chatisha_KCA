from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import CustomUser, IssueSubmissionModel
from django.core import validators

class CustomUserCreationform(UserCreationForm):
    
    # MAKE THE DEFAULT OPTIONAL FIELDS REQUIRED
    first_name = forms.CharField(required=True, max_length=20)
    last_name = forms.CharField(required=True, max_length=20)
    email = forms.EmailField(required=True, max_length=100)
    
    # SELECT ROLE TO PROCEED
    role = forms.ChoiceField(
        choices=[('', '---Please Select Role---')] + CustomUser.ROLE_CHOICE,
        required=True
    )
    
    class Meta:
        model = CustomUser
        
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'role',
            'password1',
            'password2'
        ]
    
    # VALIDATE IF EMAIL EXIST
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email already exist')
        return email

# USER LOGIN
class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )

# ISSUE SUBMISSION FORM
class IssueSubmissionForm(forms.ModelForm):
    class Meta:
        model = IssueSubmissionModel
        fields = [
            'department',
            'title',
            'description',
            'priority',
        ]