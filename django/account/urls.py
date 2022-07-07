from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    # Login
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    # My Account
    path('', views.MyAccountUpdateView.as_view(), name='myaccount'),
    path('success/', views.MyAccountUpdateSuccessTemplateView.as_view(), name='myaccount-success'),
    # Create account
    path('create/', views.UserCreateView.as_view(), name='create'),
    path('create/success/', views.UserCreateSuccessTemplateView.as_view(), name='create-success'),
    # Change password
    path('password/change/', views.PasswordChangeView.as_view(), name='change-password'),
    path('password/change/success/', views.PasswordChangeSuccessTemplateView.as_view(), name='change-password-success'),
    # Reset password - request
    path('password/reset/request/', views.PasswordResetRequestView.as_view(), name='reset-password-request'),
    path('password/reset/request/success/', views.PasswordResetRequestSuccessTemplateView.as_view(), name='reset-password-request-success'),
    # Reset password - change
    path('password/reset/change/<uidb64>/<token>/', views.PasswordResetChangeView.as_view(), name='reset-password-change'),
    path('password/reset/change/success/', views.PasswordResetChangeSuccessTemplateView.as_view(), name='reset-password-change-success'),
    # Data Import
    path('importdata/', views.ImportDataConfirmTemplateView.as_view(), name='importdata-confirm'),
    path('importdata/processing/', views.ImportDataProcessingView.as_view(), name='importdata-processing'),
    path('importdata/success/', views.ImportDataSuccessTemplateView.as_view(), name='importdata-success'),
    path('importdata/failed/', views.ImportDataFailedTemplateView.as_view(), name='importdata-failed'),
]
