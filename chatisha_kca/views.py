from django.shortcuts import render, redirect
from .forms import CustomUserCreationform, UserLoginForm, IssueSubmissionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import RedirectBasedOnRole, ROLE_TO_DEPARTMENT
from .decorators import role_required
from .models import IssueSubmissionModel, ForwardingHistoryModel, User
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

# CREATE USER REGISTRATION VIEW
def UserRegistration(request):
    if request.method == 'POST':
        r_form = CustomUserCreationform(request.POST)
        if r_form.is_valid():
            user = r_form.save()
            login(request, user)
            messages.success(request, 'You have successfully created an account. Login with username and passowrd')
            return redirect('chatisha_kca:login')
    else:
        r_form = CustomUserCreationform
    return render(request, 'chatisha_kca/register.html', {'r_form': r_form})

# LOGIN THE USER
def UserLogin(request):
    if request.method == 'POST':
        log_form = UserLoginForm(request.POST)
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
    return render(request, 'registration/login.html', {'log_form': log_form})

# LOGOUT THE USER
def UserLogout(request):
    logout(request)
    messages.success(request, 'You have logged out. Login again with username and password')
    return redirect('chatisha_kca:login')

# STAKE HOLDERS DASHBOARD
@role_required(['student', 'parent', 'sponsor', 'non_teaching_staff'])
def StakerHoldersDashboard(request, filter_by=None):
    user = request.user
    
    # DISPLAY MY SUBMITTED ISSUES
    my_issues = IssueSubmissionModel.objects.filter(user = user).order_by('-date_submitted')
    
    
    # FILTER OUT ISSUES BASED ON STATUS
    if filter_by == 'pending':
        my_issues = my_issues.filter(status = 'pending')
    elif filter_by == 'resolved':
        my_issues = my_issues.filter(status = 'resolved')
    elif filter_by == 'forwarded':
        my_issues = my_issues.filter(status = 'forwarded')
    
    # Resolved issues moved to FAQ
    elif filter_by == 'faq':
        my_issues = IssueSubmissionModel.objects.filter(status="faq").order_by('-date_submitted')
    else:
        pass
        
    return render(request, 'chatisha_kca/stake_holders_dashboard.html', {
        'my_issues' : my_issues, 
        'filter_by': filter_by or 'all',
    })

# STAKE HOLDERS CAN DELETE THE RESOLVED ISSUES, AND THE ISSUE IS STORED IN FAQ
def DeleteResolvedIssue(request, pk):
    resolved_issue = get_object_or_404(IssueSubmissionModel, pk = pk)
    if resolved_issue.status == 'resolved':
        if request.method == 'POST':
            
            resolved_issue.status = "faq"
            resolved_issue.save()
            messages.success(request, 'Issue moved to FAQ successfully')
            return redirect('chatisha_kca:stake-holders-dashboard-filter', filter_by='faq')
    return render(request, 'chatisha_kca/delete_resolved_issue.html', {'resolved_issue': resolved_issue})
        
        
# DEAN, VC & HoD DASHBOARD
@role_required(['dean_sot', 'dean_sob', 'dean_student', 'dean_school_of_education_art', 'head_of_department', 'vc'])
def DeanVcHoDDashboard(request, filter_by=None):
    user = request.user
    
    # MAP ROLE TO DEPARTMENT
    department = ROLE_TO_DEPARTMENT.get(user.role)
    
    # RETRIEVE ISSUES BASED ON THE DEPARTMENT SUBMITTED TO
    submitted_issues = IssueSubmissionModel.objects.filter(department=department).order_by('-date_submitted')
    
     # Show issues either submitted to this dean's department OR forwarded to them
    submitted_issues = IssueSubmissionModel.objects.filter(
        Q(department=department) | Q(current_owner=user)
    ).order_by('-date_submitted')
    
    # FILTER OUT ISSUES BASED ON STATUS
    if filter_by == "pending":
        submitted_issues = submitted_issues.filter(status="pending")
    elif filter_by == "resolved":
        submitted_issues = submitted_issues.filter(status="resolved")
    elif filter_by == "forwarded":
        submitted_issues = submitted_issues.filter(status="forwarded")
    else:
        pass
    
    return render(request, 'chatisha_kca/dean_vc_hod_dashboard.html', {
        'submitted_issues': submitted_issues,
        'filter_by': filter_by or 'all'
    })

# SUBMIT ISSUE - STUDENT, PARENT, SPONSORS, NON-TEACHING STAFFS.
@login_required
def SubmitIsuess(request):
    if request.method == 'POST':
        issue_form = IssueSubmissionForm(request.POST)
        if issue_form.is_valid():
            issue = issue_form.save(commit=False)
            issue.user = request.user # LINK ISSUE TO THE LOGGED IN USER.
            issue.save()
            return RedirectBasedOnRole(request.user) # DYNAMIC USER DIRECT UPON ISSUE SUBMISSION
    else:
        issue_form = IssueSubmissionForm()
    return render(request, 'chatisha_kca/submit_issue.html', {'issue_form': issue_form})

# COMPLAINT DETAIL
def IssueDetail(request, pk):
    issue_detail = get_object_or_404(IssueSubmissionModel, pk=pk)
    return render(request, 'chatisha_kca/issue_detail.html', {'issue_detail': issue_detail})

# RESPOND TO ISSUE
@role_required(['dean_sot', 'dean_sob', 'dean_student', 'dean_school_of_education_art', 'vc', 'head_of_department'])
def IssueRespond(request, pk):
    issue = get_object_or_404(IssueSubmissionModel, pk=pk)
    if request.method == "POST":
        response_text = request.POST.get("response")
        status_update = request.POST.get("status")

        issue.response = response_text
        issue.status = status_update
        issue.response_date = timezone.now()
        issue.responded_by = request.user
        
        issue.save()
        return redirect("chatisha_kca:dean-vc-hod-dashboard")
    
    return render(request, "chatisha_kca/issue_respond.html", {"issue": issue})

# FORWARD AN ISSUE TO RESPECTIVE DEAN OR VC AND VICE VERSE
@login_required
def ForwardIssue(request, pk):
    issue = get_object_or_404(IssueSubmissionModel, pk=pk)

    if request.method == "POST":
        forward_to_id = request.POST.get("forward_to")
        status_update = request.POST.get("status")
        note = request.POST.get("note")

        if forward_to_id:
            forward_to_user = get_object_or_404(User, pk=forward_to_id)

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

        return redirect("chatisha_kca:dean-vc-hod-dashboard")

    # Filter only users who can receive issues (Dean, VC, HoD)
    forwardable_users = User.objects.filter(role__in=[
        "dean_sot", "dean_sob", "dean_student",
        "dean_school_of_education_art", "vc", "head_of_department"
    ])

    return render(request, "chatisha_kca/forward_issue.html", {
        "issue": issue,
        "forwardable_users": forwardable_users
    })