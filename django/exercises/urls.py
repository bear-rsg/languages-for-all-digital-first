from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    # Exercise attempts
    path('attempt/', views.UserExerciseAttemptView.as_view(), name='attempt'),
    path('attempt/success/', views.UserExerciseAttemptSuccessTemplateView.as_view(), name='attempt-success'),

    # Exercises
    path('', views.ExerciseListView.as_view(), name='list'),
    path('add/', views.ExerciseCreateView.as_view(), name='add'),
    path('<pk>/', views.ExerciseDetailView.as_view(), name='detail'),
    path('<pk>/edit/', views.ExerciseUpdateView.as_view(), name='edit'),
    path('<pk>/delete/', views.ExerciseDeleteView.as_view(), name='delete'),
    path('copy/<pk>/', views.exercise_copy, name='copy'),

    # Exercise content
    path('<pk_exercise>/content/add/', views.ExerciseContentCreateView.as_view(), name='content-add'),
    path('<pk_exercise>/content/<pk>/edit/', views.ExerciseContentUpdateView.as_view(), name='content-edit'),
    path('<pk_exercise>/content/<pk>/delete/', views.ExerciseContentDeleteView.as_view(), name='content-delete'),

    # Export data: Excel
    path('exportdata/excel/studentscores/options/', views.ExportDataExcelStudentScoresOptionsTemplateView.as_view(), name='exportdata-excel-studentscores-options'),
    path('exportdata/excel/studentscores/', views.exportdata_excel_studentscores, name='exportdata-excel-studentscores'),

    # Export data: JSON
    path('exportdata/json/', views.ExportDataJsonTemplateView.as_view(), name='exportdata-json'),
    path('exportdata/json/studentscores/', views.exportdata_json_studentscores, name='exportdata-json-studentscores'),
    path('exportdata/json/exercises/', views.exportdata_json_exercises, name='exportdata-json-exercises'),
    path('exportdata/json/yeargroups/', views.exportdata_json_yeargroups, name='exportdata-json-yeargroups'),
    path('exportdata/json/difficulties/', views.exportdata_json_difficulties, name='exportdata-json-difficulties'),
    path('exportdata/json/languages/', views.exportdata_json_languages, name='exportdata-json-languages'),
    path('exportdata/json/fontsizes/', views.exportdata_json_fontsizes, name='exportdata-json-fontsizes'),
    path('exportdata/json/schoolclasses/', views.exportdata_json_schoolclasses, name='exportdata-json-schoolclasses'),
    path('exportdata/json/themes/', views.exportdata_json_themes, name='exportdata-json-themes'),
    path('exportdata/json/exerciseformats/', views.exportdata_json_exerciseformats, name='exportdata-json-exerciseformats'),

    # Import data: CSV
    # Exercises
    path('importdata/csv/exercises/', views.importdata_csv_exercises, name='importdata-csv-exercises'),
]
