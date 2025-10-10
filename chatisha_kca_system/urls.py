from chatisha_kca.views import CustomPasswordResetView
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('chatisha_kca.urls', namespace='chatisha_kca')),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    
    # PASSWORD RESET CONFIGURATION
    path('password_reset/', 
        CustomPasswordResetView.as_view(template_name='registration/password_reset_form.html'),
         name='password_reset'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
