from django.views.generic import TemplateView
from account import models as account_models
from exercises import models as exercises_models


class WelcomeTemplateView(TemplateView):
    """
    Class-based view to show the welcome template
    """
    template_name = 'general/welcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            exercises_todo = account_models.User.objects.get(pk=self.request.user.id).exercises_todo
            context['exercises_todo_count'] = exercises_models.Exercise.objects.filter(pk__in=exercises_todo).count()
        return context


class CookiesTemplateView(TemplateView):
    """
    Class-based view to show the cookies template
    """
    template_name = 'general/cookies.html'


class RobotsTemplateView(TemplateView):
    """
    Class-based view to show the robots.txt file
    """
    template_name = 'general/robots.txt'
    content_type = 'text/plain'
