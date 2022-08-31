from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from .apps import app_name
from . import models

admin.site.site_header = 'LFA Digital First: Dashboard'


def publish(modeladmin, request, queryset):
    """
    Sets all selected items in queryset to published
    """
    queryset.update(is_published=True)


publish.short_description = "Publish selected items (will appear on main site)"


def unpublish(modeladmin, request, queryset):
    """
    Sets all selected items in queryset to not published
    """
    queryset.update(is_published=False)


unpublish.short_description = "Unpublish selected items (will not appear on main site)"


def fk_link(object, fk_field):
    """
    Generate a link for foreign key fields in admin lists
    """
    try:
        fk = getattr(object, fk_field)  # get the foreign key object
        model_name = fk.__class__.__name__.lower().replace('_', '')
        url = reverse(f"admin:{app_name}_{model_name}_change", args=[fk.id])
        return mark_safe(f'<a href="{url}">{fk}</a>')
    except AttributeError:
        return "-"  # If FK value is null


class YearGroupAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: YearGroup
    """
    list_display = ('name', 'date_start', 'date_end', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published',)
    search_fields = ('name',)
    actions = (publish, unpublish)


class LanguageAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Language
    """
    list_display = ('name', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published',)
    search_fields = ('name',)
    actions = (publish, unpublish)


class SchoolClassUserInline(admin.TabularInline):
    model = models.SchoolClass.user_set.through
    extra = 1


class SchoolClassAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: SchoolClass
    """
    list_display = ('name', 'year_group', 'language', 'difficulty', 'teachers_names', 'students_count', 'is_active', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published', 'is_active', 'year_group', 'difficulty', 'language')
    search_fields = ('name', 'year_group__name', 'language__name', 'difficulty__name')
    fields = ('year_group', 'language', 'difficulty', 'is_active', 'is_published')
    inlines = [SchoolClassUserInline]
    actions = (publish, unpublish)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ThemeAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Theme
    """
    list_display = ('name', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published',)
    search_fields = ('name',)
    actions = (publish, unpublish)


class DifficultyAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Difficulty
    """
    list_display = ('name', 'order')
    list_display_links = ('name',)
    search_fields = ('name', 'order')

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ExerciseAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Exercise

    This blocks the model from appearing in sidebar and being able to add, edit, and delete.
    It's required in order for other ModelAdmins to include it in autocomplete_fields for searching.
    """

    search_fields = ('name',)

    def get_model_perms(self, request):
        """
        Hide from sidebar
        """
        return {}

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SchoolClassAlertExerciseAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: SchoolClassAlertExercise
    """
    list_display = ('__str__', 'fk_link_school_class', 'start_date', 'end_date', 'is_active')
    list_display_links = ('__str__',)
    autocomplete_fields = ('exercise', 'school_class')

    def fk_link_school_class(self, obj):
        return fk_link(obj, 'school_class')
    fk_link_school_class.short_description = 'School Class'
    fk_link_school_class.admin_order_field = 'school_class'


class UserExerciseAttemptAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: UserExerciseAttempt
    """
    list_display = ('__str__', 'user', 'exercise', 'score_percentage', 'attempt_duration', 'submit_timestamp')
    list_display_links = ('__str__',)
    search_fields = ('attempt_duration', 'exercise__name', 'score', 'submit_timestamp', 'user__first_name', 'user__last_name', 'user__email')
    autocomplete_fields = ('exercise',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register admin views

admin.site.register(models.YearGroup, YearGroupAdminView)
admin.site.register(models.Language, LanguageAdminView)
admin.site.register(models.SchoolClass, SchoolClassAdminView)
admin.site.register(models.Theme, ThemeAdminView)
admin.site.register(models.Difficulty, DifficultyAdminView)
admin.site.register(models.Exercise, ExerciseAdminView)

admin.site.register(models.SchoolClassAlertExercise, SchoolClassAlertExerciseAdminView)
admin.site.register(models.UserExerciseAttempt, UserExerciseAttemptAdminView)
