import xlsxwriter
import os
import glob
import time
from exercises import models


def write_data_to_worksheet(workbook, worksheet, datamatrix, column_titles=None):
    """
    Writes provided datamatrix to the provided xlsxwriter worksheet

    Provided datamatrix must be a matrix (aka list of list, 2D list)

    A list of column titles can be provided.
    """

    # If column headers written to row 0 this value will increase to 1, as data must not also be written on row 0
    column_titles_adjustment = 0
    column_max_widths = []
    column_titles_style = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#000000'})

    for row, dataitem in enumerate(datamatrix):

        # Column titles to first row, if provided
        if row == 0 and column_titles:
            for col, title in enumerate(column_titles):
                # Print column titles
                worksheet.write(row, col, title, column_titles_style)
                column_max_widths.append(len(str(title)))  # add initial values to column_max_widths list
            column_titles_adjustment = 1

        # Datamatrix
        for col, value in enumerate(dataitem):
            # Print data for each row
            worksheet.write(row + column_titles_adjustment, col, value)

            # Determine column widths
            col_width = len(str(value))
            # Set initial values in column_max_widths list, if not set in columns above
            if len(column_max_widths) <= col:
                column_max_widths.append(col_width)
            # Overwrite values in column_max_widths list if greater than them
            elif column_max_widths[col] < col_width:
                column_max_widths[col] = col_width

    # Set the column widths
    for col, cmw in enumerate(column_max_widths):
        worksheet.set_column(col, col, cmw)


def create_workbook(request):
    """
    Creates a spreadsheet and returns its file path
    """

    # Delete all existing files in the data folder
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputdata')
    files = glob.glob(data_path + '/*')
    for f in files:
        os.remove(f)
    # Establish new file name
    file_name = f'lfa_df_export_studentscores_{time.strftime("%Y-%m-%d_%H-%M")}.xlsx'
    file_path = os.path.join(data_path, file_name)
    # Create xlsxwriter workbook
    workbook = xlsxwriter.Workbook(file_path)

    # Build queryset
    # Only return student scores (i.e. not attempts by teachers and admins)
    queryset_studentscores = models.UserExerciseAttempt.objects.filter(user__role__name='student')
    # Filter by classes, if param is provided
    filter_classes = request.GET.getlist('filter_classes', '')
    if filter_classes:
        queryset_studentscores = queryset_studentscores.filter(user__classes__in=filter_classes)
    # Improve performance
    queryset_studentscores = queryset_studentscores.select_related(
        'exercise',
        'exercise__language',
        'exercise__exercise_format',
        'exercise__theme',
        'exercise__difficulty',
        'user'
    )

    # Create worksheet
    column_titles_print = [
        "Exercise ID",
        "Exercise URL",
        "Exercise Language",
        "Exercise Format",
        "Exercise Theme",
        "Exercise Difficulty",
        "Student Email",
        "Student ID",
        "Score",
        "Attempt Detail",
        "Attempt Duration (milliseconds)",
        "Submit Timestamp"
    ]

    data_print = []
    for studentscore in queryset_studentscores:
        data_print.append([
            studentscore.exercise.id,
            request.build_absolute_uri(f'/exercises/{studentscore.exercise.id}'),
            str(studentscore.exercise.language),
            str(studentscore.exercise.exercise_format),
            str(studentscore.exercise.theme),
            str(studentscore.exercise.difficulty),
            studentscore.user.email,
            studentscore.user.internal_id_number,
            studentscore.score,
            studentscore.attempt_detail,
            studentscore.attempt_duration,
            studentscore.submit_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ])
    write_data_to_worksheet(workbook, workbook.add_worksheet("Student Scores"), data_print, column_titles_print)

    # Close workbook and return its file path
    workbook.close()
    return file_path
