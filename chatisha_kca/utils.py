from django.shortcuts import redirect
from .models import CustomUser, IssueSubmissionModel, ForwardingHistoryModel, Notification
from django.utils import timezone
from datetime import timedelta

# REDIRECT USERS BASED ON ROLES
def RedirectBasedOnRole(user):
    role_redirects = {
        
        # STAKEHOLDER
        'student': 'chatisha_kca:stake-holders-dashboard',
        'parent': 'chatisha_kca:stake-holders-dashboard',
        'sponsor': 'chatisha_kca:stake-holders-dashboard',
        'non_teaching_staff': 'chatisha_kca:stake-holders-dashboard',
        
        # HEAD OF DEPARTMENT
        'hod_bsd': 'chatisha_kca:dean-vc-hod-dashboard',
        'hod_bac': 'chatisha_kca:dean-vc-hod-dashboard',
        'hod_bbit': 'chatisha_kca:dean-vc-hod-dashboard',
        'hod_bit': 'chatisha_kca:dean-vc-hod-dashboard',
        
        # DEAN
        'dean_sot': 'chatisha_kca:dean-vc-hod-dashboard',
        'dean_sob': 'chatisha_kca:dean-vc-hod-dashboard',
        'dean_student': 'chatisha_kca:dean-vc-hod-dashboard',
        'dean_school_of_education_art': 'chatisha_kca:dean-vc-hod-dashboard',
        
        # VC
        'vc':'chatisha_kca:dean-vc-hod-dashboard',

    }
    if user.role in role_redirects:
        return redirect(role_redirects[user.role])
    return redirect('chatisha_kca:login') # FALLBACK IF ROLE NOT RECOGNIZED

# DEAN, VC, HOD ROLE -> DEPARTMENT
ROLE_TO_DEPARTMENT = {
    
    # HEAD OF DEPARTMENT
    'hod_bsd' : 'bsd',
    'hod_bac' : 'bac',
    'hod_bbit' : 'bbit',
    'hod_bit' : 'bit',
    
    # DEAN
    'dean_sot' : 'sot',
    'dean_student': 'dos',
    'dean_sob': 'sob',
    'dean_school_of_education_art': 'sea',
    
    # VC
    'vc': 'vc_ceo',
}

# WHO SHOULD FORWARD TO WHO
ALLOWED_FORWARD = {
    
    # HoD FORWARD TO DEAN
    'hod_bsd': ['dean_sot'],
    'hod_bac': ['dean_sot'],
    'hod_bbit': ['dean_sot'],
    'hod_bit': ['dean_sot'],
    
    # DEAN FORWARD TO VC
    'dean_sot': ['vc'],
    'dean_student': ['vc'],
    'dean_sob': ['vc'],
    'dean_school_of_education_art': ['vc'],
    
    # VC CANOT FORWARD FURTHER
    'vc': [],
}

# ESCALTE OVERDUE ISSUE FROM HoD TO DEAN DASHBOARD
def get_forwardable_user(current_user):
    allowed_role = ALLOWED_FORWARD.get(current_user.role, [])
    return CustomUser.objects.filter(role__in = allowed_role)

def auto_forward_overdue_issue():
    # Get all pending issues older than 2 days
    overdue_issues = IssueSubmissionModel.objects.filter(
        status="pending",
        current_owner__role__startswith="hod_",
        date_submitted__lte=timezone.now() - timedelta(minutes = 2)
    )

    for issue in overdue_issues:
        hod = issue.current_owner

        # Find the first dean available (you can refine mapping later)
        dean = CustomUser.objects.filter(role__startswith="dean_").first()
        
        if dean:
            
            # Save forwarding history
            ForwardingHistoryModel.objects.create(
                issue=issue,
                forwarded_by=hod,
                forwarded_to=dean,
                note="Automatically forwarded because issue overstayed."
            )

            # Update issue
            issue.current_owner = dean
            issue.status = "forwarded"
            issue.save()
            
            # NOFIFY THE USERS INVOLVED
            Notification.objects.create(
                user=dean,
                issue=issue,
                message=f'Issue "{issue.title}" was auto-forwarded to you from {hod.get_role_display()} after no action was taken.'
            )
            Notification.objects.create(
                user=issue.user,
                issue=issue,
                message=f'Your issue "{issue.title}" was escalated from {hod.get_role_display()} to {dean.get_role_display()} after no response.'
            )
        
    # ESCALATE OVERDUE ISSUE FROM DEAN TO VC DASHBOARD
    overdue_dean_issues = IssueSubmissionModel.objects.filter(
        status="forwarded",
        current_owner__role__startswith="dean_",
        date_submitted__lte=timezone.now() - timedelta(minutes=10)  # maybe longer wait
    )

    for issue in overdue_dean_issues:
        dean = issue.current_owner
        vc = CustomUser.objects.filter(role="vc").first()

        if vc:
            ForwardingHistoryModel.objects.create(
                issue=issue,
                forwarded_by=dean,
                forwarded_to=vc,
                note="Automatically escalated to VC because issue overstayed."
            )
            issue.current_owner = vc
            issue.status = "forwarded"
            issue.save()

            # Notifications
            Notification.objects.create(
                user=issue.user,
                issue=issue,
                message=f'Your issue "{issue.title}" was escalated from {dean.get_role_display()} to {vc.get_role_display()} after no response.'
            )
            Notification.objects.create(
                user=vc,
                issue=issue,
                message=f'Issue "{issue.title}" was auto-forwarded from {dean.get_role_display()} to you ({vc.get_role_display()}) after no action was taken.'
            )
