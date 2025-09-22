from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.contrib.auth import get_user_model

# CREATE USERS
class CustomUser(AbstractUser):
    ROLE_CHOICE = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('sponsor', 'Sponsor'),
        ('dean_sot', 'Dean school of Technology'),
        ('vc', 'VC'),
        ('head_of_department', 'Head of department'),
        ('non_teaching_staff', 'Non-teaching Staff'),
        ('dean_student', 'Dean of Student'),
        ('dean_sob', 'Dean school of Business'),
        ('dean_school_of_education_art', 'Dean School of Education & Art'),
    ]
    
    role = models.CharField(max_length=200, choices=ROLE_CHOICE)

User = get_user_model()

# CREATE DEPARTMENT CHOICES
DEPARTMENT_CHOICES = [
    ('sea', 'School of education & Art'),
    ('dos', 'Dean of Student'),
    ('sob', 'School of Business'),
    ('sot', 'School of Technology'),
    ('vc_ceo', 'VC & CEO'),
    ('head_department', 'Head of Department'),
]

# ISSUE PRORITY CHOICES
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
    ('faq', 'FAQ'),
]

# ISSUE SUBMISSION FORM
class IssueSubmissionModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # USER WHO SUBMITTED THE ISSUE
    department = models.CharField(max_length=255, choices=DEPARTMENT_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    date_submitted = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # ISSUE RESPONSE
    response = models.TextField(blank=True, null=True)
    response_date = models.DateTimeField(blank=True, null=True)
    responded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="responses"
    
    )
    
    # TRACK WHO HAS THE ISSUE NOW
    current_owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="current_issues"
    )
    
    def __str__(self):
        return f"{self.user}, {self.title}, {self.department}"

# FORWARD ISSUE FROM ONE DEPARTMENT TO AN OTHER
class ForwardingHistoryModel(models.Model):
    issue = models.ForeignKey(IssueSubmissionModel, on_delete=models.CASCADE, related_name="forwarding_history")
    forwarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="forwarded_from")
    forwarded_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="forwarded_to")
    note = models.TextField(blank=True, null=True)  # Optional reason
    date_forwarded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.forwarded_by} → {self.forwarded_to} ({self.issue.title})"
    
