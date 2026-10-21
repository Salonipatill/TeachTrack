from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth
from ClassApp import views
urlpatterns = [path('admin/', admin.site.urls), path('', include('ClassApp.urls')),
 path('accounts/login/', views.sign_in, name='login'), path('accounts/register/', views.register, name='register'),
 path('accounts/logout/', auth.LogoutView.as_view(), name='logout'),
 path('accounts/password/change/', auth.PasswordChangeView.as_view(template_name='form.html', extra_context={'title':'Change password'}), name='password_change'),
 path('accounts/password/change/done/', auth.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done')]
