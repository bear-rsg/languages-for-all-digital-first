from django.contrib import admin
from account import forms
from .models import User, UserRole
from django.contrib.auth.forms import UserChangeForm


class UserAdmin(admin.ModelAdmin):
    """
    Customise the admin interface: User
    """

    add_form = forms.DashboardUserChangeForm
    form = UserChangeForm
    model = User
    list_display = ['username',
                    'first_name',
                    'last_name',
                    'email',
                    'role',
                    'is_active']
    list_filter = ['role', 'is_active']
    readonly_fields = ['username']


class UserRoleAdmin(admin.ModelAdmin):
    """
    Customise the admin interface: UserRole
    """

    list_display = ['name',]


# Register
admin.site.register(User, UserAdmin)
admin.site.register(UserRole, UserRoleAdmin)
