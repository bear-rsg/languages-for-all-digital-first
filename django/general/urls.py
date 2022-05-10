from django.urls import path
from . import views

app_name = 'general'

urlpatterns = [
    path('', views.WelcomeTemplateView.as_view(), name='welcome'),
    path('cookies/', views.CookiesTemplateView.as_view(), name='cookies')
]
