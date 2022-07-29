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

    # Export data: student scores
    path('exportdata/studentscores/options/', views.ExportDataStudentScoresOptionsTemplateView.as_view(), name='export-studentscores-options'),
    path('exportdata/studentscores/', views.exportdata_studentscores, name='export-studentscores'),
]
