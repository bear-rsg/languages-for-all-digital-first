from django.db import migrations
from django.core.management.sql import emit_post_migrate_signal
from django.db import transaction
from account import models


"""
This data migration adds default data for the following models:

- Groups
- Permissions
- UserRoles

Note that they must come in this order due to dependencies
"""


def insert_groups(apps, schema_editor):
    """
    Inserts user Group
    Groups used for setting permissions
    This function must come before inserting users, as users get added to groups when saved
    """

    groups = [
        {
            "name": "teacher_permissions_group"
        },
        {
            "name": "guest_permissions_group"
        }
    ]

    Group = apps.get_model("auth", "Group")
    for group in groups:
        with transaction.atomic():
            Group(**group).save()


def add_group_permissions(apps,schema_editor):
    """
    Add relevant permissions to specified group

    As permissions are set following initial migration,
    the few bits of extra lines are needed to ensure that permissions have been created
    """

    # Ensure permissions and content types have been created.
    db_alias = schema_editor.connection.alias
    emit_post_migrate_signal(2, False, db_alias)

    # Recommended way to get Group and Permission (vs importing)
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model('auth', "Permission")

    # List of permissions (view, add, change, delete) for each model within each app for each group
    group_permissions_list = [
        {
            "group_name": "teacher_permissions_group",
            "apps": [
                {
                    "app_name": "exercises",
                    "models": [
                        {
                            "model_name": "schoolclassalertexercise",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "schoolclass",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "difficulty",
                            "permissions": []
                        },
                        {
                            "model_name": "exercise",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "exerciseformat",
                            "permissions": ['view',]
                        },
                        {
                            "model_name": "exerciseformatfillintheblank",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "exerciseformatimagematch",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "exerciseformattranslation",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "exerciseformatmultiplechoice",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "exerciseformatsentencebuilder",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "exerciseformatexternal",
                            "permissions": ['view', 'add', 'change', 'delete']
                        },
                        {
                            "model_name": "language",
                            "permissions": []
                        },
                        {
                            "model_name": "theme",
                            "permissions": []
                        },
                        {
                            "model_name": "userexerciseattempt",
                            "permissions": ['view']
                        }
                    ]
                }
            ]
        },
        {
            "group_name": "guest_permissions_group",
            "apps": [
                {
                    "app_name": "exercises",
                    "models": [
                        {
                            "model_name": "schoolclassalertexercise",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "schoolclass",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "difficulty",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exercise",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exerciseformat",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exerciseformatfillintheblank",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exerciseformatimagematch",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exerciseformattranslation",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exerciseformatmultiplechoice",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exerciseformatsentencebuilder",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "exerciseformatexternal",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "language",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "theme",
                            "permissions": ['view']
                        },
                        {
                            "model_name": "userexerciseattempt",
                            "permissions": ['view']
                        }
                    ]
                }
            ]
        }
    ]

    # Loop through group > app > model > permission to define all of the permissions set in group_permissions_list
    for group in group_permissions_list:
        g = Group.objects.get(name=group['group_name'])
        for app in group['apps']:
            a = app['app_name']
            for model in app['models']:
                m = model['model_name']
                for permission in model['permissions']:
                    g.permissions.add(Permission.objects.get(codename=f"{permission}_{m}", content_type__app_label=a))


def insert_user_roles(apps, schema_editor):
    """
    Inserts UserRole objects
    """

    roles = [
        { "name": "admin" },
        { "name": "student" },
        { "name": "teacher" },
        { "name": "guest" }
    ]

    for role in roles:
        with transaction.atomic():
            models.UserRole(**role).save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_initial'),
        ('exercises', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_groups),
        migrations.RunPython(add_group_permissions),
        migrations.RunPython(insert_user_roles)
    ]
