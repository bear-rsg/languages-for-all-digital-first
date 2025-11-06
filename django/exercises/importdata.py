from . import models
from django.db import transaction


def import_exercises(exercises):
    """
    Creates new Exercise and related objects in db

    Parameters:
    exercises = a dict of Exercise data and related data (e.g. ExerciseFormatX)

    Returns:
    status = True, if import was successful. False, if an error occurred.
    msg = Explanation of status, e.g. success confirmation or error details.
    """

    try:
        # Uses an atomic block, so if any errors occur, no data will be created
        with transaction.atomic():

            count_exercises = 0

            for exercise in exercises:

                exercise_obj = models.Exercise.objects.create(
                    name=exercise.name,
                    language=models.Language.objects.get(name=exercise.language),
                    exercise_format=models.ExerciseFormat.objects.get(name=exercise.language),
                )
                count_exercises += 1

                if exercise.exercise_format.lower() == 'image match':
                    for fd in exercise.format_data:
                        models.ExerciseFormatImageMatch.objects.create(
                            name=fd.name
                        )

            return True, f"Successfully processed {count_exercises} exercise records."

    except Exception as e:
        return False, f"Error occurred. No data has been created. Details: {e}"
