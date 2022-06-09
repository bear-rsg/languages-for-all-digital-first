from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [

    # General app's urls
    path('', include('general.urls')),
    path('', include('exercises.urls')),

    # Account app's urls + Django's built in auth's urls
    # Share same pattern (/account) for consistency for user
    # Account app's urls must appear above Django's auth's urls to take priority
    path('account/', include('account.urls')),
    path('account/', include('django.contrib.auth.urls')),

    # Django admin
    path('dashboard/', admin.site.urls),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
