from django.db import migrations
from help import models


def insert_help_items(apps, schema_editor):
    """
    Inserts objects into specified model
    """

    objects = [
        {
            "name": "Sample pdf help file",
            "pdf": "help-pdf/sample.pdf",
            "admin_published": True
        },
        {
            "name": "Example video for helping demo the website to users",
            "video": "https://www.youtube.com/watch?v=m80E1K75vDI",
            "admin_published": True
        },
        {
            "name": "Here's an example link for the help section",
            "link": "https://www.birmingham.ac.uk/index.aspx",
            "admin_published": True
        },
    ]

    for object in objects:
        models.HelpItem(**object).save()


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_help_items),
    ]
