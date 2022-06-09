from django.db import migrations
from exercises import models
from django.db import transaction


"""
This data migration adds default data for the following models:
- Language
- Difficulty
- Exercise format
- Theme
- School class
"""


def insert_languages(apps, schema_editor):
    """
    Inserts Language objects
    """

    languages = [
        "Portuguese",
        "French",
        "Spanish",
        "Italian",
        "Japenese",
    ]

    for language in languages:
        models.Language(name=language).save()


def insert_difficulties(apps, schema_editor):
    """
    Inserts Difficulty objects
    """

    difficulties = [
        {"name": "Beginners", "order": 1, "colour_hex": "#2ecc71"},
        {"name": "Intermediate", "order": 2, "colour_hex": "#f39c12"},
        {"name": "Advanced", "order": 3, "colour_hex": "#c23616"}
    ]

    for difficulty in difficulties:
        models.Difficulty(**difficulty).save()


def insert_exercise_formats(apps, schema_editor):
    """
    Inserts ExerciseFormat objects
    """

    formats = [
        {
            "name": "Image Match",
            "icon": '<i class="fas fa-images"></i>',
            "instructions": "Choose the correct label for each image",
            "is_marked_automatically_by_system": True
        },
        {
            "name": "Multiple Choice",
            "icon": '<i class="fas fa-list-ul"></i>',
            "instructions": "Choose the correct answer of 4 possible options",
            "is_marked_automatically_by_system": True
        },
        {
            "name": "Fill in the Blank",
            "icon": '<i class="fas fa-edit"></i>',
            "instructions": "Fill in the blank words in the sentence. Hover over an (i) icon to reveal the answer.",
            "is_marked_automatically_by_system": True
        },
        {
            "name": "Sentence Builder",
            "icon": '<i class="fas fa-tools"></i>',
            "instructions": "Build the correctly translated sentence from the available words",
            "is_marked_automatically_by_system": True
        },
        {
            "name": "Translation",
            "icon": '<i class="fas fa-scroll"></i>',
            "instructions": "Translate the source material and self-mark against the provided correct translation",
            "is_marked_automatically_by_system": False
        },
        {
            "name": "External",
            "icon": '<i class="fas fa-external-link-square-alt"></i>',
            "instructions": "Click on the link to complete the external exercise",
            "is_marked_automatically_by_system": False
        }
    ]

    for format in formats:
        models.ExerciseFormat(**format).save()


def insert_themes(apps, schema_editor):
    """
    Inserts Theme objects.
    """

    themes = [
        "Test theme 1",
        "Test theme 2"
    ]

    for theme in themes:
        with transaction.atomic():
            models.Theme(name=theme).save()


def insert_school_class(apps, schema_editor):
    """
    Inserts SchoolClass objects
    """

    school_classes = [
        {
            "language": models.Language.objects.get(name='Portuguese'),
            "difficulty": models.Difficulty.objects.get(name="Beginners")
        },
    ]

    for school_class in school_classes:
        models.SchoolClass(**school_class).save()


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_languages),
        migrations.RunPython(insert_difficulties),
        migrations.RunPython(insert_exercise_formats),
        migrations.RunPython(insert_themes),
        migrations.RunPython(insert_school_class)
    ]
