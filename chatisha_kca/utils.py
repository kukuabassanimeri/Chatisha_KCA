from django.shortcuts import redirect
from .models import CustomUser, IssueSubmissionModel, ForwardingHistoryModel, Notification
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

# REDIRECT USERS BASED ON ROLES
def RedirectBasedOnRole(user):
    role_redirects = {
        
        # STAKEHOLDER
        'student': 'chatisha_kca:stake-holders-dashboard',
        
        # HoD AND CoD
        'admin_assistant' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'faculty_manager' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'hod_time_tabling' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'cod_nac' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'hod_exam_nac' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'cod_sdis' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'hod_exam_sdis' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'cod_dsai' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'hod_exam_sdai' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'hod_student_attachment' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        'hod_projects' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        
        # DEAN
        'dean_sot': 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        
        # DVC
        'dvc_asa' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',
        
        # VC
        'vc' : 'chatisha_kca:hod-cod-dean-dvc-vc-dashboard',

    }
    if user.role in role_redirects:
        return redirect(role_redirects[user.role])
    return redirect('chatisha_kca:login') # FALLBACK IF ROLE NOT RECOGNIZED

# HoD,CoD, DEAN, DVC, VC ROLE -> DEPARTMENT
ROLE_TO_DEPARTMENT = {
    
    # HoD AND CoD
    'admin_assistant' : 'admin',
    'faculty_manager' : 'faculty',
    'hod_time_tabling' : 'hodtt',
    'cod_nac' : 'codnac',
    'hod_exam_nac' : 'hodexamnac',
    'cod_sdis' : 'codsdis',
    'hod_exam_sdis' : 'hodexamsdis',
    'cod_dsai' : 'coddsai',
    'hod_exam_sdai' : 'hodexamdsai',
    'hod_student_attachment' : 'hodstudentattachment',
    'hod_projects' : 'hodprojects',
    
    # DEAN
    'dean_sot' : 'deansot',
    
    # DVC
    'dvc_asa' : 'dvcasa',
    
    # VC
    'vc': 'vc_ceo',
}

# WHO SHOULD FORWARD TO WHO
ALLOWED_FORWARD = {
    
    # HoD AND CoD FORWARD TO DEAN
    'cod_nac' : ['dean_sot'],
    'hod_exam_nac' : ['dean_sot'],
    'cod_sdis' : ['dean_sot'],
    'hod_exam_sdis' : ['dean_sot'],
    'cod_dsai' : ['dean_sot'],
    'hod_exam_sdai' : ['dean_sot'],
    
    # DEAN FORWARD TO DVC
    'dean_sot': ['dvc_sot'],
    
    # DVC FORWARD VC
    'dvc_asa': ['vc'],
    
    # VC NO FORWARDING
    'vc' : [],
}

# AUTO-ESCALATING OVERDUE ISSUES

# ESCALTE OVERDUE ISSUE FROM HoD TO DEAN DASHBOARD
def get_forwardable_user(current_user):
    allowed_role = ALLOWED_FORWARD.get(current_user.role, [])
    return CustomUser.objects.filter(role__in = allowed_role)

def auto_forward_overdue_issue():
    
    # Get all pending issues older than number of days.
    overdue_issues = IssueSubmissionModel.objects.filter(
        status="pending",
        date_submitted__lte=timezone.now() - timedelta(days = 5)
    ).filter(
        Q(current_owner__role__startswith='hod_') | 
        Q(current_owner__role__startswith='cod_')
    )

    def get_overstayed_duration(issue):
        # THE NUMBER OF DAYS ISSUE OVERSTAYED
       
        days = (timezone.now() - issue.date_submitted).days
        return f"{days} day{'s' if days != 1 else ''}" if days > 0 else "less than a day"
        
        # Now testing with Minutes.
        
        #delta = timezone.now() - issue.date_submitted
        #minutes = delta.seconds // 60
        #return f"{minutes} minute{'s' if minutes != 1 else ''}" if minutes > 0 else "less than a minute"

    for issue in overdue_issues:
        hod = issue.current_owner

        # Find the first dean available
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
                message=f'{issue.title} was auto-forwarded to you from {hod.get_role_display()} after no action was taken for {get_overstayed_duration(issue)}.'
            )
            Notification.objects.create(
                user=issue.user,
                issue=issue,
                message=f'{issue.title} was escalated from {hod.get_role_display()} to {dean.get_role_display()} after no response for {get_overstayed_duration(issue)}.'
            )
        
    # ESCALATE OVERDUE ISSUE FROM DEAN TO DVC DASHBOARD
    overdue_dean_issues = IssueSubmissionModel.objects.filter(
        status="forwarded",
        current_owner__role__startswith="dean_",
        date_submitted__lte=timezone.now() - timedelta(days = 5)  # maybe longer wait
    )

    for issue in overdue_dean_issues:
        dean = issue.current_owner
        dvc = CustomUser.objects.filter(role="dvc_asa").first()

        if dvc:
            ForwardingHistoryModel.objects.create(
                issue=issue,
                forwarded_by=dean,
                forwarded_to=dvc,
                note="Automatically escalated to DVC because issue overstayed."
            )
            issue.current_owner = dvc
            issue.status = "forwarded"
            issue.save()

            # Notifications
            Notification.objects.create(
                user=issue.user,
                issue=issue,
                message=f'{issue.title} was escalated from {dean.get_role_display()} to {dvc.get_role_display()} after no response for {get_overstayed_duration(issue)}.'
            )
            Notification.objects.create(
                user=dvc,
                issue=issue,
                message=f'{issue.title} was auto-forwarded from {dean.get_role_display()} to you after no action was taken for {get_overstayed_duration(issue)}.'
            )
            
    # ESCALATE OVERDUE ISSUE FROM DVC TO VC DASHBOARD
    overdue_dvc_issues = IssueSubmissionModel.objects.filter(
        status="forwarded",
        current_owner__role__startswith="dvc_",
        date_submitted__lte=timezone.now() - timedelta(days = 5)  # maybe longer wait
    )

    for issue in overdue_dvc_issues:
        dvc = issue.current_owner
        vc = CustomUser.objects.filter(role="vc").first()

        if vc:
            ForwardingHistoryModel.objects.create(
                issue=issue,
                forwarded_by=dvc,
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
                message=f'{issue.title} was escalated from {dvc.get_role_display()} to {vc.get_role_display()} after no response for {get_overstayed_duration(issue)}.'
            )
            Notification.objects.create(
                user=vc,
                issue=issue,
                message=f'{issue.title} was auto-forwarded from {dvc.get_role_display()} to you after no action was taken for {get_overstayed_duration(issue)}.'
            )
            