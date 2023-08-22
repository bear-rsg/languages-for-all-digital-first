from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group
from account import forms
from .models import User, UsersImportSpreadsheet


class UsersImportSpreadsheetAdmin(admin.ModelAdmin):
    """
    Customise the admin interface: UsersImportSpreadsheet
    """

    model = UsersImportSpreadsheet
    list_display = ['spreadsheet_filename', 'id', 'lastupdated']
    list_display_links = ['spreadsheet_filename']
    readonly_fields = ['lastupdated']


class UserAdmin(DjangoUserAdmin):
    """
    Customise the admin interface: User
    """

    add_form = forms.DashboardUserChangeForm
    form = UserChangeForm
    model = User
    list_display = ['username',
                    'internal_id_number',
                    'first_name',
                    'last_name',
                    'email',
                    'role',
                    'default_language',
                    'is_internal',
                    'is_active',
                    'date_joined',
                    'last_login']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    list_filter = ['role', 'is_active', 'is_internal']
    filter_horizontal = ('classes',)
    readonly_fields = ['date_joined', 'last_login', 'is_staff', 'is_superuser']
    fields = ('username',
              'first_name',
              'last_name',
              'role',
              'is_internal',
              'internal_id_number',
              'is_staff',
              'is_superuser',
              'classes',
              'is_active',
              'date_joined',
              'last_login')
    fieldsets = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        # Only allow changes to the password
        if '/password/' in request.get_full_path():
            return True
        else:
            return False


# Register above ModelAdmins
admin.site.register(UsersImportSpreadsheet, UsersImportSpreadsheetAdmin)
admin.site.register(User, UserAdmin)

# Unregister the Group
admin.site.unregister(Group)
