from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django import forms
from .models import User, UserRole
from captcha.fields import ReCaptchaField, ReCaptchaV3
from exercises.models import SchoolClass


class DashboardUserChangeForm(UserChangeForm):
    """
    Form to specify fields in the user change form, which is only accessible via the Django admin
    It's used in admin.py
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'default_language', 'classes')


class PublicUserChangeForm(UserChangeForm):
    """
    Form to specify fields in the user change form, which is accessible through the public website
    As anyone can use this form (i.e. students) 'role' is excluded so they can't change their role
    It's used in views.py
    """

    # Hide password, as template gives a direct link to it styled more appropriately
    password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # removes : from label, e.g. Email: becomes Email
        self.fields['default_language'].help_text = "The main language that you're registered to study/teach within Languages for All. Exercises will be filtered by this language by default."

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'default_language')


class PublicPasswordChangeForm(PasswordChangeForm):
    """
    Form to specify fields in the password change form, which is accessible through the public website
    It's used in views.py
    """

    # Hide password, as template gives a direct link to it styled more appropriately
    password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # removes : from label, e.g. Email: becomes Email
        self.fields['new_password1'].help_text = "Your password:<br>- can't be too similar to your other personal information.<br>- must contain at least 8 characters.<br>- can't be a commonly used password.<br>- cant be entirely numeric."

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'default_language', 'classes')
