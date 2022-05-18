from django.db import migrations
from django.db import transaction
from account import models


def insert_user_roles(apps, schema_editor):
    """
    Inserts UserRole objects
    """

    roles = [
        { "name": "admin", },
        { "name": "student", },
        { "name": "teacher", }
    ]

    for role in roles:
        with transaction.atomic():
            models.UserRole(**role).save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_user_roles)
    ]
