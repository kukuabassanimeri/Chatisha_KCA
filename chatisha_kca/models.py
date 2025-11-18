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
        
        # HoD AND CoD ROLE
        ('admin_assistant', 'Admin Assistant'),
        ('faculty_manager', 'Faculty Manager'),
        ('hod_time_tabling', 'HoD Timetabling'),
        ('cod_nac', 'CoD NAC'),
        ('hod_exam_nac', 'HoD Exam NAC'),
        ('cod_sdis', 'CoD SDIS'),
        ('hod_exam_sdis', 'HoD Exam SDIS'),
        ('cod_dsai', 'CoD SDAI'),
        ('hod_exam_sdai', 'HoD Exam SDAI'),
        ('hod_student_attachment', 'HoD Student Attachment'),
        ('hod_projects', 'HoD Projects'),
        
        # DEAN ROLE
        ('dean_sot', 'Dean SOT'),
        
        # DVC
        ('dvc_asa', 'DVC ASA'),
        
        # VC ROLE
        ('vc', 'VC'),
    ]
  
    role = models.CharField(max_length=200, choices=ROLE_CHOICE)

User = get_user_model()

DEPARTMENT_CHOICES = [
    
    # HoD and CoD  
    ('admin', 'Admin Assistant'),
    ('faculty', 'Faculty Manager'),
    ('hodtt', 'HoD Timetabling'),
    ('codnac', 'CoD NAC'),
    ('hodexamnac', 'HoD Exam Nac'),
    ('codsdis', 'CoD SDIS'),
    ('hodexamsdis', 'HoD Exam SDIS'),
    ('coddsai', 'CoD DSAI'),
    ('hodexamdsai', 'HoD Exam DSAI'),
    ('hodstudentattachment', 'HoD Student Attachment'),
    ('hodprojects', 'HoD Projects'),
    
    # DEAN
    ('deansot', 'Dean SOT'),
    
    # DVC
    ('dvcasa', 'DVC ASA'),    
    
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
    note = models.TextField(max_length = 100, default= 'Reason')
    date_forwarded = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.forwarded_by} → {self.forwarded_to} ({self.issue.title})'
    
# FAQ MODEL
class FAQModel(models.Model):
    question = models.TextField(unique = True) # The original question description.
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