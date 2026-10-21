from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth
from ClassApp import views
urlpatterns = [path('admin/', admin.site.urls), path('', include('ClassApp.urls')),
 path('accounts/login/', views.sign_in, name='login'), path('accounts/register/', views.register, name='register'),
 path('accounts/logout/', auth.LogoutView.as_view(), name='logout'),
 path('accounts/password/change/', auth.PasswordChangeView.as_view(template_name='form.html', extra_context={'title':'Change password'}), name='password_change'),
 path('accounts/password/change/done/', auth.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
 path('accounts/password/reset/', auth.PasswordResetView.as_view(template_name='form.html', extra_context={'title':'Reset password'}), name='password_reset'),
 path('accounts/password/reset/done/', auth.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
 path('accounts/password/reset/<uidb64>/<token>/', auth.PasswordResetConfirmView.as_view(template_name='form.html', extra_context={'title':'Choose a new password'}), name='password_reset_confirm'),
 path('accounts/password/reset/complete/', auth.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete')]

urlpatterns += [path(prefix+'-forgot_password/',auth.PasswordResetView.as_view(template_name='form.html',extra_context={'title':'Reset password'}),name=prefix+'_forgot_password') for prefix in ['student','faculty','director']]
