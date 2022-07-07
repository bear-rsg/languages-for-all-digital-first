from django.views.generic import (TemplateView, CreateView, UpdateView, RedirectView)
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (PasswordChangeView, PasswordResetView, PasswordResetConfirmView)
from django.urls import reverse
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from account import (forms, models)
from exercises.models import UserExerciseAttempt
import pandas as pd
import os
import random
import string


class MyAccountUpdateView(LoginRequiredMixin, UpdateView):
    """
    Class-based view to show the 'my account' template
    This allows users to update their own details,
    which is why it's an UpdateView and uses get_object to specify current user
    """

    template_name = 'account/myaccount.html'
    model = models.User
    form_class = forms.PublicUserChangeForm
    success_url = reverse_lazy('account:myaccount-success')

    def get_object(self):
        """
        Return the current user
        """
        return self.model.objects.get(pk=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(MyAccountUpdateView, self).get_context_data(**kwargs)
        # Exercise history
        context['exercise_attempts'] = UserExerciseAttempt.objects.filter(user=self.get_object())
        return context


class MyAccountUpdateSuccessTemplateView(TemplateView):
    """
    Class-based view to show the 'my account' success template
    This is when the user updates their account details on the 'my account' page
    """

    template_name = 'account/myaccount-success.html'


class UserCreateView(CreateView):
    """
    Class-based view to show the account create template
    """

    template_name = 'account/create.html'
    form_class = forms.PublicUserCreationForm
    success_url = reverse_lazy('account:create-success')

    def form_valid(self, form):

        # Save the new user
        self.object = form.save(commit=False)
        self.object.save()

        # Add the many to many relationships with classes
        for c in form.cleaned_data['classes']:
            self.object.classes.add(c)

        return super().form_valid(form)


class UserCreateSuccessTemplateView(TemplateView):
    """
    Class-based view to show the account create success template
    """

    template_name = 'account/create-success.html'


class PasswordChangeView(PasswordChangeView):
    """
    Class-based view to show the password change template
    """

    form_class = forms.PublicPasswordChangeForm
    template_name = 'registration/change-password.html'
    success_url = reverse_lazy('account:change-password-success')


class PasswordChangeSuccessTemplateView(TemplateView):
    """
    Class-based view to show the password change success template
    """

    template_name = 'registration/change-password-success.html'


class PasswordResetRequestView(PasswordResetView):
    """
    Class-based view to show the password reset request template
    """

    template_name = 'registration/reset-password-request.html'
    email_template_name = 'registration/reset-password-request-email.txt'
    subject_template_name = 'registration/reset-password-request-subject.txt'
    success_url = reverse_lazy('account:reset-password-request-success')


class PasswordResetRequestSuccessTemplateView(TemplateView):
    """
    Class-based view to show the password reset request success template
    """

    template_name = 'registration/reset-password-request-success.html'


class PasswordResetChangeView(PasswordResetConfirmView):
    """
    Class-based view to show the password reset change template
    """

    template_name = 'registration/reset-password-change.html'
    success_url = reverse_lazy('account:reset-password-change-success')


class PasswordResetChangeSuccessTemplateView(TemplateView):
    """
    Class-based view to show the password reset change success template
    """

    template_name = 'registration/reset-password-change-success.html'


class ImportDataConfirmTemplateView(LoginRequiredMixin, TemplateView):
    """
    Class-based view to show the import data confirmation template
    Requires user to be logged in
    """

    login_url = '/dashboard/'
    template_name = 'account/importdata-confirm.html'


class ImportDataProcessingView(LoginRequiredMixin, RedirectView):
    """
    Class-based view to execute the data import and redirect user to success/failed page
    Requires user to be logged in
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """
        This method imports new user data from the latest Excel spreadsheet

        Returns a success page or an error page (and emails software developer with error if found)
        """

        try:
            # Get users data from latest Excel spreadsheet
            spreadsheet_obj = models.UsersImportSpreadsheet.objects.order_by('-lastupdated').first()
            users = pd.read_excel(os.path.join(settings.MEDIA_ROOT, spreadsheet_obj.spreadsheet.name)).to_dict('records')
            # Add each new user to database and email instructions to them
            for user in users:
                # Determines if new
                if not models.User.objects.filter(email=user['email']).count():
                    # Generate password (mix of letters and numbers) 10 chars long
                    characters = string.ascii_letters + string.digits
                    password_plain = ''.join(random.choice(characters) for i in range(10))
                    user['password'] = make_password(password_plain)
                    # Assign Foreign Keys
                    user['role'] = models.UserRole.objects.get(name=user['role'])
                    # Create user in db
                    with transaction.atomic():
                        models.User(**user).save()
                    # Email user with instructions
                    send_mail('subjecthere',
                           f"""Hi {user['first_name']},

Welcome to Languages for All - Digital First! You've been registered with a new {user['role']} account.

Please go to https://lfa-digitalfirst.bham.ac.uk/account/login/ where you can login with the following details:

Username: {user['email']}
Password: {password_plain}

Please note that you must change this password after logging in for the first time. If you have any issues you can email us for support at {settings.ADMIN_EMAIL}

Thanks,
Languages for All Team
""",
                            settings.DEFAULT_FROM_EMAIL,
                            (user['email'],),
                            fail_silently=True)

            print('Completed data import process successfully')

            # If successfully ran, redirect user to success page
            return reverse('account:importdata-success')

        except Exception as e:
            print(f'Data import process failed with error: {e}')
            # Send email alert to software developer
            send_mail('Languages for All - Digital First: Import Data error',
                      f"An error occurred when {self.request.user} tried importing user data into the Languages for All - Digital First database.\n\nThe following error was returned:\n\n{e}",
                      settings.DEFAULT_FROM_EMAIL,
                      (settings.EMAIL_HOST_USER,),
                      fail_silently=True)
            # Redirect user to failed page and show the error message
            messages.error(self.request, e)
            return reverse('account:importdata-failed')


class ImportDataSuccessTemplateView(LoginRequiredMixin, TemplateView):
    """
    Class-based view to show the import data success template
    Requires user to be logged in
    """

    template_name = 'account/importdata-success.html'


class ImportDataFailedTemplateView(LoginRequiredMixin, TemplateView):
    """
    Class-based view to show the import data failed template
    Requires user to be logged in
    """

    template_name = 'account/importdata-failed.html'
