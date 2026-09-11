from django.urls import path

from api.views import (
    CsrfCookieView,
    DeleteAccountView,
    LoginView,
    LogoutView,
    MeView,
    ProfileUpdateView,
    RegisterView,
    PasswordResetConfirmView,
    PasswordResetRequestView
)

urlpatterns = [
    path("csrf/", CsrfCookieView.as_view(), name="auth-csrf"),
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("profile/", ProfileUpdateView.as_view(), name="auth-profile-update"),
    path("delete/", DeleteAccountView.as_view(), name="auth-delete-account"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
]