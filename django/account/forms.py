from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django import forms
from .models import User, UserRole
from captcha.fields import ReCaptchaField, ReCaptchaV3
from exercises.models import SchoolClass


class DashboardUserCreationForm(UserCreationForm):
    """
    Form to specify fields in the dashboard user creation form
    E.g. this form appears when editing users in the Django admin dashboard
    It's used in admin.py
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name',
                  'last_name',
                  'email',
                  'role',
                  'default_language',
                  'classes',)


class DashboardUserChangeForm(UserChangeForm):
    """
    Form to specify fields in the user change form, which is only accessible via the Django admin
    It's used in admin.py
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role', 'default_language', 'classes')


class PublicUserCreationForm(UserCreationForm):
    """
    Form to specify fields in the user (student) creation form on the public website
    Role is ommitted as this will be set in the view, as users shouldn't choose their own role
    It's used in views.py
    """

    # M2M relationship with SchoolClass
    classes = forms.ModelMultipleChoiceField(
        queryset=SchoolClass.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all classes that you're registered on",
        required=False
    )

    # Google ReCaptcha v3
    captcha = ReCaptchaField(widget=ReCaptchaV3, label='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # removes : from label, e.g. Email: becomes Email
        self.fields['default_language'].help_text = "The main language that you're registered to study/teach within Languages for All. Exercises will be filtered by this language by default."
        self.fields['password1'].help_text = "Your password:<br>- can't be too similar to your other personal information.<br>- must contain at least 8 characters.<br>- can't be a commonly used password.<br>- can't be entirely numeric."

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email', 'default_language', 'classes')

    def clean_email(self):
        """
        Check that the email provided doesn't already exist
        """
        cleaned_data = self.clean()
        e = cleaned_data.get('email')
        # If this email exists
        if len(User.objects.filter(email=e)) > 0:
            self.add_error('email', "There's already an account associated with this email address")
        return e


class PublicUserChangeForm(UserChangeForm):
    """
    Form to specify fields in the user change form, which is accessible through the public website
    As anyone can use this form (i.e. students) 'role' is excluded so they can't change their role
    It's used in views.py
    """

    # M2M relationship with SchoolClass
    classes = forms.ModelMultipleChoiceField(
        queryset=SchoolClass.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select all classes that you're registered on",
        required=False
    )

    # Hide password, as template gives a direct link to it styled more appropriately
    password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""  # removes : from label, e.g. Email: becomes Email
        self.fields['default_language'].help_text = "The main language that you're registered to study/teach within Languages for All. Exercises will be filtered by this language by default."

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'default_language', 'classes')


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
