from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth import get_user_model
from django import forms

# CREATE USERS
class CustomUser(AbstractUser):
    
    ROLE_CHOICE = [
        
        # STAKEHOLDER ROLE
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('sponsor', 'Sponsor'),
        ('non_teaching_staff', 'Non-teaching Staff'),
        
        # HoD ROLE
        ('hod_bsd', 'Head of department BSD'),
        ('hod_bac', 'Head of Department BAC'),
        ('hod_bbit', 'Head of Department BBIT'),
        ('hod_bit', 'Head of Department BIT'),
        
        # DEAN ROLE
        ('dean_sot', 'Dean school of Technology'),
        ('dean_student', 'Dean of Student'),
        ('dean_sob', 'Dean school of Business'),
        ('dean_school_of_education_art', 'Dean School of Education & Art'),
        
        # VC ROLE
        ('vc', 'VC'),
    ]
  
    role = models.CharField(max_length=200, choices=ROLE_CHOICE)

User = get_user_model()

DEPARTMENT_CHOICES = [
    
    # HoD
    ('bsd', 'Head of Department BSD'),
    ('bac', 'Head of Department BAC'),
    ('bbit', 'Head of Department BBIT'),
    ('bit', 'Head of Department BIT'),
    
    # DEAN
    ('sot', 'Dean School of Technology'),
    ('dos', 'Dean of Students'),
    ('sob', 'Dean School of Business'),
    ('sea', 'Dean School of education & Art'),
    
    # VC
    ('vc_ceo', 'VC & CEO'),
]

PRIORITY_CHOICES = [
    ('high', 'High'),
    ('medium', 'Medium'),
    ('low', 'Low'),
]

# ISSUE STATUS CHOICES
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('resolved', 'Resolved'),
    ('forwarded', 'Forwarded'),
]

# ISSUE SUBMISSION MODEL
class IssueSubmissionModel(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)  # USER WHO SUBMITTED THE ISSUE
    department = models.CharField(max_length = 255, choices = DEPARTMENT_CHOICES)
    title = models.CharField(max_length = 255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices = PRIORITY_CHOICES)
    date_submitted = models.DateTimeField(default = timezone.now)
    status = models.CharField(max_length = 20, choices = STATUS_CHOICES, default = 'pending')
    
    # ISSUE RESPONSE
    response = models.TextField(blank = True, null = True)
    response_date = models.DateTimeField(blank = True, null = True)
    responded_by = models.ForeignKey(
        User, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'responses'
    
    )
    
    # TRACK WHO HAS THE ISSUE NOW
    current_owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_issues'
    )
    
    # MOVE DELETED ISSUE TO FAQ 
    moved_to_faq = models.BooleanField(default=False)
    

    def __str__(self):
        return f'{self.user}, {self.title}, {self.department}'
    
    
# FORWARD ISSUE FROM ONE DEPARTMENT TO AN OTHER
class ForwardingHistoryModel(models.Model):
    issue = models.ForeignKey(IssueSubmissionModel, on_delete=models.CASCADE, related_name='forwarding_history')
    forwarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='forwarded_from')
    forwarded_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='forwarded_to')
    note = models.TextField(blank=True, null=True)
    date_forwarded = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.forwarded_by} → {self.forwarded_to} ({self.issue.title})'
    
# FAQ MODEL
class FAQModel(models.Model):
    question = models.TextField() # The original question description.
    answer = models.TextField() # The resolved respond.
    
    def __str__(self):
        return self.question[:50]

# NOTIFICATION
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name = 'notifications')
    issue = models.ForeignKey(IssueSubmissionModel, on_delete = models.CASCADE)
    message = models.CharField(max_length = 255)
    is_read = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True, blank = True, null = True)
    
    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:30]}"