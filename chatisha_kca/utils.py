from django.shortcuts import redirect

# REDIRECT USERS BASED ON ROLES
def RedirectBasedOnRole(user):
    role_redirects = {
        'student': 'chatisha_kca:stake-holders-dashboard',
        'parent': 'chatisha_kca:stake-holders-dashboard',
        'sponsor': 'chatisha_kca:stake-holders-dashboard',
        'non_teaching_staff': 'chatisha_kca:stake-holders-dashboard',
        
        # DEAN, VC, HEAD OF DEPARTMENT TO BE REDIRECTED TO ONE DASHBOARD ON LOGIN
        'dean_sot': 'chatisha_kca:dean-vc-hod-dashboard',
        'dean_sob': 'chatisha_kca:dean-vc-hod-dashboard',
        'dean_student': 'chatisha_kca:dean-vc-hod-dashboard',
        'dean_school_of_education_art': 'dean-vc-hod-dashboard',
        'vc':'chatisha_kca:dean-vc-hod-dashboard',
        'head_of_department':'chatisha_kca:dean-vc-hod-dashboard'
    }
    if user.role in role_redirects:
        return redirect(role_redirects[user.role])
    return redirect('chatisha_kca:login') # FALLBACK IF ROLE NOT RECOGNIZED

# DEAN, VC, HOD ROLE -> DEPARTMENT
ROLE_TO_DEPARTMENT = {
    'dean_sot': 'sot',
    'dean_sob': 'sob',
    'dean_student': 'dos',
    'dean_school_of_education_art': 'sea',
    'vc': 'vc_ceo',
    'head_of_department': 'head_department'
}
  