from django.urls import path
from . import views

app_name = 'chatisha_kca' # appname 

urlpatterns = [
    
    # REGISTRATION AND LOGIN URLS
    path('signup/', views.UserRegistration, name='register'),
    path('login/', views.UserLogin, name='login'),
    path('logout/', views.UserLogout, name='logout'),
    
    # DASHBOARD URLS
    path('stakeholdersdashboard/', views.StakeHoldersDashboard, name='stake-holders-dashboard'),
    path('stakeholdersdashboard/<str:filter_by>/', views.StakeHoldersDashboard, name='stake-holders-dashboard-filter'),
    
    path('deanvchoddashboard/', views.DeanVcHoDDashboard, name='dean-vc-hod-dashboard'),
    path('deanvchoddashboard/<str:filter_by>/', views.DeanVcHoDDashboard, name='dean-vc-hod-dashboard-filter'),
    
    # ISSUE SUBMISSION URLS
    path('submitissue/', views.SubmitIssue, name='submit-issue'),
    path('issuedetail/<int:pk>/', views.IssueDetail, name='issue-detail'),
    
    # ACTION ON ISSUE
    path('issuerespond/<int:pk>/', views.IssueRespond, name='issue-respond'),
    path('forwardissue/<int:pk>/', views.ForwardIssue, name='forward-issue'),
    path('deleteresolvedissue/delete/<int:pk>/', views.DeleteResolvedIssue, name='delete-resolved-issue'),
    
    # FAQ
    path('faq/', views.FAQList, name='faq'),   
    
    # NOTIFICATION
    path('notification/<int:pk>/', views.view_notification, name = 'view-notification')
    
]