from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from . import sitemaps

sitemaps = {
    'static-pages': sitemaps.StaticPagesSitemap,

    'help:list': sitemaps.HelpItemListSitemap,
    'help:detail': sitemaps.HelpItemDetailSitemap,

    'exercises:list': sitemaps.ExerciseListSitemap,
    'exercises:detail': sitemaps.ExerciseDetailSitemap
}

urlpatterns = [

    # General app's urls
    path('', include('general.urls')),
    path('exercises/', include('exercises.urls')),
    path('help/', include('help.urls')),

    # Account app's urls + Django's built in auth's urls
    # Share same pattern (/account) for consistency for user
    # Account app's urls must appear above Django's auth's urls to take priority
    path('account/', include('account.urls')),
    path('account/', include('django.contrib.auth.urls')),

    # Django admin
    path('dashboard/', admin.site.urls),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
