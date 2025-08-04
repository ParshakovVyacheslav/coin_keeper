from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm, ResetPasswordForm, ResetPasswordConfirmForm, ChangePasswordForm

urlpatterns = [
    path(
        'login/', 
        views.CustomLoginView.as_view(), 
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/logged_out.html'), name='logout'),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path(
        'password_reset/', 
        auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html',
                                             form_class=ResetPasswordForm), 
        name='password_reset'
    ),
    path(
        'password_reset_done/', 
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
        name='password_reset_done'
    ),
    path(
        'password_reset_confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html',
                                                    form_class=ResetPasswordConfirmForm), 
        name='password_reset_confirm'
    ),
    path(
        'password_reset_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
        name='password_reset_complete'
    ),
    path(
        'password_change/', 
        auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html',
                                              form_class=ChangePasswordForm), 
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
        name='password_change_done',
    ),
    path('profile/', views.profile, name='profile'),
    path('edit_profile', views.ProfileEditView.as_view(), name='edit_profile')
]
