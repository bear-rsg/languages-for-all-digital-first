from django.views.generic import (TemplateView, CreateView, UpdateView)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (PasswordChangeView, PasswordResetView, PasswordResetConfirmView)
from account import (forms, models)


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
        form.instance.role = models.UserRole.objects.get(name='student')

        # Save the new user
        self.object = form.save(commit=False)
        self.object.save()

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
