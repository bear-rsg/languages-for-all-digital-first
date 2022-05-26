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


class LanguageAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Language
    """
    list_display = ('name', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published',)
    search_fields = ('name',)
    actions = (publish, unpublish)


class SchoolClassAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: SchoolClass
    """
    list_display = ('name',  'language', 'difficulty', 'teachers_names', 'students_count', 'is_active', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published', 'is_active', 'difficulty', 'language')
    search_fields = ('name', 'language__name', 'difficulty__name')
    actions = (publish, unpublish)


class ThemeAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Theme
    """
    list_display = ('name_full', 'is_published')
    list_display_links = ('name_full',)
    list_filter = ('is_published',)
    search_fields = ('name',)
    actions = (publish, unpublish)


class DifficultyAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Difficulty
    """
    list_display = ('name', 'order', 'colour_hex')
    list_display_links = ('name',)
    search_fields = ('name', 'order', 'colour_hex')


class ExerciseAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: Exercise
    """

    search_fields = ('name',)

    def get_model_perms(self, request):
        """
        Hide SL tables from admin side bar, but still CRUD via inline shortcuts on main models
        """
        return {}


class ExerciseFurtherStudyMaterialAdminView(admin.ModelAdmin):
    """
    Customise the admin interface: ExerciseFurtherStudyMaterial
    """
    list_display = ('exercise', 'name', 'file', 'url', 'is_published')
    list_display_links = ('name',)
    list_filter = ('is_published',)
    exclude = ('created_by',)
    search_fields = ('name', 'file', 'url')
    actions = (publish, unpublish)

    def get_queryset(self, request):
        # Superuser (aka admin) can see all
        if request.user.is_superuser:
            return models.ExerciseFurtherStudyMaterial.objects.all()
        # Non superuser (aka teachers) can only see if they own the parent exercise it
        else:
            try:
                return models.ExerciseFurtherStudyMaterial.objects.filter(exercise__owned_by=request.user.id)
            except None:
                return models.ExerciseFurtherStudyMaterial.objects.none()

    def get_form(self, request, obj=None, **kwargs):
        # Customise the Add form only (not the Change form)
        if not obj:
            kwargs.update({
                'exclude': ('created_by',),
            })
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # If creating an object (i.e. not updating an existing object)
        if obj.created_by is None:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


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
    search_fields = ('__str__',)
    autocomplete_fields = ('exercise',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register admin views

admin.site.register(models.Language, LanguageAdminView)
admin.site.register(models.SchoolClass, SchoolClassAdminView)
admin.site.register(models.Theme, ThemeAdminView)
admin.site.register(models.Difficulty, DifficultyAdminView)
admin.site.register(models.Exercise, ExerciseAdminView)

admin.site.register(models.ExerciseFurtherStudyMaterial, ExerciseFurtherStudyMaterialAdminView)
admin.site.register(models.SchoolClassAlertExercise, SchoolClassAlertExerciseAdminView)
admin.site.register(models.UserExerciseAttempt, UserExerciseAttemptAdminView)
