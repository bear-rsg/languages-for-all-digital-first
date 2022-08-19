from django.db import migrations
from exercises import models
from django.db import transaction


"""
This data migration adds default data for the following models:
- Year group
- Language
- Difficulty
- Exercise format
- Theme
- School class
"""


def insert_year_groups(apps, schema_editor):
    """
    Inserts YearGroup objects.
    """

    year_groups = [
        {
            "name": "2022/23",
            "date_start": "2022-09-01",
            "date_end": "2023-08-31",
            "is_published": True
        },
        {
            "name": "2023/24",
            "date_start": "2023-09-01",
            "date_end": "2024-08-31"
        },
        {
            "name": "2024/25",
            "date_start": "2024-09-01",
            "date_end": "2025-08-31"
        },
        {
            "name": "2025/26",
            "date_start": "2025-09-01",
            "date_end": "2026-08-31"
        },
        {
            "name": "2026/27",
            "date_start": "2026-09-01",
            "date_end": "2027-08-31"
        },
    ]

    for year_group in year_groups:
        models.YearGroup(**year_group).save()


def insert_languages(apps, schema_editor):
    """
    Inserts Language objects
    """

    languages = [
        "Portuguese",
        "French",
        "Spanish",
        "Italian",
        "Japanese",
    ]

    for language in languages:
        models.Language(name=language).save()


def insert_difficulties(apps, schema_editor):
    """
    Inserts Difficulty objects
    """

    difficulties = [
        {"name": "Level 1", "order": 1},
        {"name": "Level 2", "order": 2},
        {"name": "Level 3", "order": 3},
        {"name": "Level 4", "order": 4},
        {"name": "Level 5", "order": 5},
        {"name": "Level 6", "order": 6},
        {"name": "Level 7", "order": 7},
        {"name": "Level 8", "order": 8},
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
            "instructions": "Choose the correct answer of the available possible options",
            "is_marked_automatically_by_system": True
        },
        {
            "name": "Fill in the Blank",
            "icon": '<i class="fas fa-edit"></i>',
            "instructions": "Fill in the blank words in the sentence. Answers arecase sensitive. Hover over an (i) icon to reveal the answer.",
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
    initial_year_group = models.YearGroup.objects.get(name='2022/23')

    school_classes = [
        {
            "year_group": initial_year_group,
            "language": models.Language.objects.get(name='Portuguese'),
            "difficulty": models.Difficulty.objects.get(name="Level 1")
        },
        {
            "year_group": initial_year_group,
            "language": models.Language.objects.get(name='Portuguese'),
            "difficulty": models.Difficulty.objects.get(name="Level 3")
        },
    ]

    for school_class in school_classes:
        models.SchoolClass(**school_class).save()


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_year_groups),
        migrations.RunPython(insert_languages),
        migrations.RunPython(insert_difficulties),
        migrations.RunPython(insert_exercise_formats),
        migrations.RunPython(insert_themes),
        migrations.RunPython(insert_school_class)
    ]
