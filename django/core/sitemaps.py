from django.contrib.sitemaps import Sitemap
from help import models as helpmodels
from exercises import models as exercisesmodels
from django.urls import reverse


class StaticPagesSitemap(Sitemap):
    """
    Sitemap: Static pages that have no data models (e.g. welcome, some about pages, etc.)
    """

    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return ['general:welcome',
                'general:cookies']

    def location(self, obj):
        return reverse(obj)


class HelpItemListSitemap(Sitemap):
    """
    Sitemap: HelpItem List
    """

    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ['help:list']

    def location(self, obj):
        return reverse(obj)


class HelpItemDetailSitemap(Sitemap):
    """
    Sitemap: HelpItem Detail
    """

    priority = 0.5

    def items(self):
        return helpmodels.HelpItem.objects.filter(admin_published=True)


class ExerciseListSitemap(Sitemap):
    """
    Sitemap: Exercise List
    """

    changefreq = "daily"
    priority = 1.0

    def items(self):
        return ['exercises:list']

    def lastmod(self, obj):
        try:
            return exercisesmodels.Exercise.objects.order_by('-created_datetime')[0].created_datetime
        except Exception:
            return None

    def location(self, obj):
        return reverse(obj)


class ExerciseDetailSitemap(Sitemap):
    """
    Sitemap: Exercise Detail
    """

    priority = 1.0

    def items(self):
        return exercisesmodels.Exercise.objects.filter(is_published=True)
