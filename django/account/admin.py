from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group
from .models import User, UsersImportSpreadsheet


def delete_users(modeladmin, request, queryset):
    """
    Deletes all selected users
    """
    queryset.delete()


delete_users.short_description = "PERMANENTLY DELETE selected users from database"


def users_active(modeladmin, request, queryset):
    """
    Sets all selected users in queryset as 'active'
    """
    queryset.update(is_active=True)


users_active.short_description = "Make selected users 'active' (they can login)"


def users_inactive(modeladmin, request, queryset):
    """
    Sets all selected users in queryset as 'inactive'
    """
    queryset.update(is_active=False)


users_inactive.short_description = "Make selected users 'inactive' (they can not login)"


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

    form = UserChangeForm
    model = User
    list_display = ['username',
                    'internal_id_number',
                    'first_name',
                    'last_name',
                    'role',
                    'is_internal',
                    'is_active',
                    'date_joined',
                    'last_login']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'internal_id_number']
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
    actions = (users_active, users_inactive, delete_users)
    ordering = ['first_name', 'last_name']

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
