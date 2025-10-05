from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import CustomUser, IssueSubmissionModel
from django.core import validators
import re

class CustomUserCreationform(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=20)
    last_name = forms.CharField(required=True, max_length=20)
    email = forms.EmailField(required=True, max_length=100)

    # Select Role to Proceed
    role = forms.ChoiceField(
        choices=[('', 'Please Select Role')] + CustomUser.ROLE_CHOICE,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Common field styling
        common_style = {'class': 'form-control'}

        self.fields['first_name'].widget = forms.TextInput(attrs={**common_style, 'placeholder': 'First Name'})
        self.fields['last_name'].widget = forms.TextInput(attrs={**common_style, 'placeholder': 'Last Name'})
        self.fields['username'].widget = forms.TextInput(attrs={**common_style, 'placeholder': 'Username'})
        self.fields['email'].widget = forms.EmailInput(attrs={**common_style, 'placeholder': 'Email Address'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={**common_style, 'placeholder': 'Password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={**common_style, 'placeholder': 'Confirm Password'})

        # Style the role select field
        self.fields['role'].widget.attrs.update({
            'class': 'form-select',
        })
        
        # Remove label suffix
        self.label_suffix = ''

    # CHECK IF USERNAME & EMAIL EXIST
    
    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if CustomUser.objects.filter(username = username).exists():
            raise forms.ValidationError('This username already exit')
        return username
        
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email = email).exists():
            raise forms.ValidationError('This email already exists')
        return email

    # VALIDATE PASSWORD STRENGTH
    def clean_password1(self):
        password = self.cleaned_data.get('password1')

        # Must be at least 8 characters
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')

        # Must contain uppercase
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')

        # Must contain lowercase
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Password must contain at least one lowercase letter.')

        # Must contain digits
        if not re.search(r'\d', password):
            raise forms.ValidationError('Password must contain at least one number.')

        # Must contain special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError('Password must contain at least one special character.')
        
        return password
    
    # CHECK IF PASSWORD1 AND PASSWORD2 DON'T MATCH
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
    
    
# USER LOGIN
class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    
    def __init__(self, *args, **kwargs): # DEFINE CONSTRUCTOR
        super().__init__(*args, **kwargs) # *args and **kwargs - Accept any number of positional & keyword arguments.
        # Calls the parent class constructor.
        self.label_suffix = '' # Changes that default colon by setting the label suffix to an empty string ('').

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
        
    # WHEN SUBMITTING ISSUE, START FROM HoD
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter department choices to only HODs
        hod_departments = ['bsd', 'bac', 'bbit', 'bit']
        hod_choices = [choice for choice in IssueSubmissionModel._meta.get_field('department').choices if choice[0] in hod_departments]

        self.fields['department'] = forms.ChoiceField(
            choices=[('', 'Select Department')] + hod_choices,
            label="Submit to Head of Department"
        )