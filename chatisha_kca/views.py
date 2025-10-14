from django.shortcuts import render, redirect
from .forms import CustomUserCreationform, UserLoginForm, IssueSubmissionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import RedirectBasedOnRole, ROLE_TO_DEPARTMENT, get_forwardable_user, auto_forward_overdue_issue
from .decorators import role_required
from .models import (IssueSubmissionModel, ForwardingHistoryModel, User, FAQModel, CustomUser, Notification, UserProfile)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView

# CREATE USER REGISTRATION VIEW
def UserRegistration(request):
    if request.method == 'POST':
        r_form = CustomUserCreationform(request.POST)
        if r_form.is_valid():
            user = r_form.save()
            login(request, user)
            messages.success(request, 'Account created successfully. Login with username and password')
            return redirect('chatisha_kca:login')
    else:
        r_form = CustomUserCreationform()
    return render(request, 'chatisha_kca/register.html', {'r_form': r_form})

# LOGIN THE USER
def UserLogin(request):
    if request.method == 'POST':
        log_form = UserLoginForm(request.POST)
        
        reset_form = PasswordResetForm()
        
        if log_form.is_valid():       
            username = log_form.cleaned_data['username']
            password = log_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)

                # REDIRECT USERS TO SPECIFIC DASHBOARD BASED ON THE ROLES
                messages.success(request, 'You are currently logged in.')
                return RedirectBasedOnRole(user)
            else:
                messages.error(request, 'Invalid username or password')
    else:
        log_form = UserLoginForm()  
        reset_form = PasswordResetForm()        
    return render(request, 'registration/login.html', {'log_form': log_form, 'reset_form' : reset_form})

# LOGOUT THE USER
def UserLogout(request):
    logout(request)
    messages.success(request, 'You have logged out.')
    return redirect('chatisha_kca:login')

# STAKE HOLDERS DASHBOARD
@role_required([
    'student', 
    'parent', 
    'sponsor', 
    'non_teaching_staff',
    ])
def StakeHoldersDashboard(request, filter_by=None):
    user = request.user
    
    # DISPLAY SUBMITTED ISSUES
    my_issues = IssueSubmissionModel.objects.filter(user = user, moved_to_faq=False).order_by('-date_submitted')
    
    # NOTIFICATIONS
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    
    # KEEP TRACK OF ALL SUBMITTED ISSUES
    total_issue = my_issues.count()
    
    # KEEP TRACK OF ALL PENDING / RESOLVED / FORWARDEDSSUES
    total_pending_issue = my_issues.filter(status = 'pending').count()
    total_resolved_issue = my_issues.filter(status = 'resolved').count()
    total_forwarded_issue = my_issues.filter(status = 'forwarded').count()
    
    # FILTER OUT ISSUES BASED ON STATUS
    if filter_by == 'pending':
        my_issues = my_issues.filter(status ='pending')
    elif filter_by == 'resolved':
        my_issues = my_issues.filter(status ='resolved')
    elif filter_by ==  'forwarded':
        my_issues = my_issues.filter(status= 'forwarded')
    else:
        pass
        
    return render(request, 'chatisha_kca/stake_holders_dashboard.html', {
        'my_issues' : my_issues, 
        'filter_by': filter_by or 'all',
        'total_issue': total_issue,
        'total_pending_issue': total_pending_issue,
        'total_resolved_issue': total_resolved_issue,
        'total_forwarded_issue': total_forwarded_issue,
        'notifications': notifications,
        'unread_count': unread_count,
        'issue_form' : IssueSubmissionForm()
    })

# STAKE HOLDERS CAN DELETE THE RESOLVED ISSUES, AND THE ISSUE IS STORED IN FAQ
def DeleteResolvedIssue(request, pk):
    resolved_issue = get_object_or_404(IssueSubmissionModel, pk = pk)
    if resolved_issue.status == 'resolved':
        if request.method == 'POST':
            
            # STORE DELETE ISSUES IN FAQ
            FAQModel.objects.create(
                question=resolved_issue.description,
                answer=resolved_issue.response or 'No response provided'
            )
            
            # Remove from student's view (but still remains in admin report)
            resolved_issue.moved_to_faq = True
            resolved_issue.save()
            
            #resolved_issue.delete()
            messages.success(request, 'Issue moved to FAQ successfully')
            return redirect('chatisha_kca:stake-holders-dashboard')
    return render(request, 'chatisha_kca/delete_resolved_issue.html', {'resolved_issue': resolved_issue})
           
# HoD, DEAN, & VC DASHBOARD
@role_required([
    
    # HoD
    'hod_bsd',
    'hod_bac',
    'hod_bbit',
    'hod_bit',
    
    # DEAN
    'dean_sot',  
    'dean_student',
    'dean_sob',
    'dean_school_of_education_art',
    
    #VC
    'vc',
])

def DeanVcHoDDashboard(request, filter_by=None):
    user = request.user
    
    auto_forward_overdue_issue()
    
    # MAP ROLE TO DEPARTMENT
    department = ROLE_TO_DEPARTMENT.get(user.role)
    
    # Show issues either submitted to this dean's department OR forwarded to them
    submitted_issues = IssueSubmissionModel.objects.filter(
        Q(department=department) | Q(current_owner=user)
    ).order_by('-date_submitted')
    
    # NOTIFY ADMINS FOR INCOMING ISSUE.
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    # KEEP TRACK OF ALL SUBMITTED ISSUES
    total_issue = submitted_issues.count()
    
    # KEEP TRACK OF ALL PENDING / RESOLVED / FORWARDED ISSUES
    total_pending = submitted_issues.filter(status = 'pending').count()
    total_resolved = submitted_issues.filter(status = 'resolved').count()
    total_forwarded = submitted_issues.filter(status = 'forwarded').count()
    
    # FILTER OUT ISSUES BASED ON STATUS
    if filter_by == 'pending':
        submitted_issues = submitted_issues.filter(status='pending')
    elif filter_by == 'resolved':
        submitted_issues = submitted_issues.filter(status='resolved')
    elif filter_by == 'forwarded':
        submitted_issues = submitted_issues.filter(status='forwarded')
    else:
        pass
    
    return render(request, 'chatisha_kca/dean_vc_hod_dashboard.html', {
        'submitted_issues': submitted_issues,
        'filter_by': filter_by or 'all',
        'total_issue': total_issue,
        'total_pending': total_pending,
        'total_resolved': total_resolved,
        'total_forwarded': total_forwarded,
        'notifications': notifications,
        'unread_count': unread_count
    })

# SUBMIT ISSUE - STUDENT, PARENT, SPONSORS, NON-TEACHING STAFFS.
@login_required
def SubmitIssue(request):
    if request.method == 'POST':
        issue_form = IssueSubmissionForm(request.POST)
        if issue_form.is_valid():
            issue = issue_form.save(commit=False)
            issue.user = request.user # LINK ISSUE TO THE LOGGED IN USER.
            
            # Assign current_owner based on selected department
            hod_role_map = {
                'bsd': 'hod_bsd',
                'bac': 'hod_bac',
                'bbit': 'hod_bbit',
                'bit': 'hod_bit',
            }
            selected_dept = issue_form.cleaned_data['department']
            hod_user = CustomUser.objects.filter(role=hod_role_map[selected_dept]).first()
            
            if hod_user:
                issue.current_owner = hod_user
                issue.save()
                
                # Create notification for the HOD
                Notification.objects.create(
                    user=hod_user,
                    issue=issue,
                    message=f'New issue {issue.title} has been raised by {request.user.get_role_display()}.'
                )
                
                messages.success(request, 'Issue submitted successfully to HOD.')
                return RedirectBasedOnRole(request.user) # DYNAMIC USER DIRECT UPON ISSUE SUBMISSION
            
            else:
                messages.error(request, 'Cannot submit: No HOD assigned for the selected department.')
                return redirect('chatisha_kca:submit-issue')
    else:
        issue_form = IssueSubmissionForm()
    return render(request, 'chatisha_kca/submit_issue.html', {'issue_form': issue_form})

# COMPLAINT DETAIL
def IssueDetail(request, pk):
    issue_detail = get_object_or_404(IssueSubmissionModel, pk=pk)
    return render(request, 'chatisha_kca/issue_detail.html', {'issue_detail': issue_detail})

# HoD, DEAN, VC RESPOND TO ISSUE
@role_required([
    
    # HoD
    'hod_bsd',
    'hod_bac',
    'hod_bbit',
    'hod_bit',
    
    # DEAN
    'dean_sot', 
    'dean_student',
    'dean_sob',  
    'dean_school_of_education_art', 
    
    # VC
    'vc',
])
def IssueRespond(request, pk):
    issue = get_object_or_404(IssueSubmissionModel, pk=pk)
    if request.method == 'POST':
        response_text = request.POST.get('response')
        status_update = request.POST.get('status')

        issue.response = response_text
        issue.status = status_update
        issue.response_date = timezone.now()
        issue.responded_by = request.user
        
        issue.save()
        
        # Notify stakeholder 
        Notification.objects.create(
            user=issue.user,
            issue=issue,
            message=f'{issue.title} has been {status_update} by {request.user.get_role_display()}'
        )
        
        # Notify whole forwarding chain if RESOLVED
        if status_update == "resolved":
            forwarding_chain = issue.forwarding_history.all()
            notified_users = set()

            for f in forwarding_chain:
                if f.forwarded_by not in notified_users:
                    Notification.objects.create(
                        user=f.forwarded_by,
                        issue=issue,
                        message=f'{issue.title} you forwarded has been resolved by {request.user.get_role_display()}.'
                    )
                    notified_users.add(f.forwarded_by)

        return redirect('chatisha_kca:dean-vc-hod-dashboard')
    
    return render(request, 'chatisha_kca/issue_respond.html', {'issue': issue})

# FORWARD AN ISSUE TO RESPECTIVE HoD, DEAN OR VC AND VICE VERSE
@login_required
def ForwardIssue(request, pk):
    issue = get_object_or_404(IssueSubmissionModel, pk=pk)

    if request.method == 'POST':
        forward_to_id = request.POST.get('forward_to')
        status_update = request.POST.get('status')
        note = request.POST.get('note')

        if forward_to_id:
            forward_to_user = get_object_or_404(CustomUser, pk=forward_to_id)

            # Save forwarding history
            ForwardingHistoryModel.objects.create(
                issue=issue,
                forwarded_by=request.user,
                forwarded_to=forward_to_user,
                note=note
            )

            # Update issue
            issue.status = status_update
            issue.current_owner = forward_to_user
            issue.save()
            
            # Notify stakeholder
            Notification.objects.create(
                user=issue.user,
                issue=issue,
                message=f' {issue.title} has been {status_update} to {forward_to_user.get_role_display()}.'
            )
            
             # Notify new owner (Dean, VC, etc.)
            Notification.objects.create(
                user=forward_to_user,
                issue=issue,
                message=f'{issue.title} has been forwarded to you by {request.user.get_role_display()}.'
            )

        return redirect('chatisha_kca:dean-vc-hod-dashboard')

    # Filter only users who can receive issues (HoD, Dean, VC)
    forwardable_users = get_forwardable_user(request.user)

    return render(request, 'chatisha_kca/forward_issue.html', {
        'issue': issue,
        'forwardable_users': forwardable_users
    })

# FAQ VIEW
def FAQList(request):
    faqs = FAQModel.objects.all() # FILTER ALL FAQ
    return render(request, 'chatisha_kca/faq.html', {'faqs': faqs })

# STAKEHOLDER NOTIFICATION
def view_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    
    # Redirect user back to their correct dashboard
    if request.user.role in ['student', 'parent', 'sponsor', 'non_teaching_staff']:
        return redirect('chatisha_kca:stake-holders-dashboard')
    else:
        return redirect('chatisha_kca:dean-vc-hod-dashboard')

# PASSWORD RESET
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('chatisha_kca:login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset link sent, please check your email!')
        return super().form_valid(form)