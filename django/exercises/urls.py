from django.urls import path
from . import views

app_name = 'exercises'

urlpatterns = [
    # Exercise attempts
    path('exercises/attempt/', views.UserExerciseAttemptView.as_view(), name='attempt'),
    path('exercises/attempt/success/', views.UserExerciseAttemptSuccessTemplateView.as_view(), name='attempt-success'),

    # Exercises
    path('exercises/', views.ExerciseListView.as_view(), name='list'),
    path('exercises/add/', views.ExerciseCreateView.as_view(), name='add'),
    path('exercises/<pk>/', views.ExerciseDetailView.as_view(), name='detail'),
    path('exercises/<pk>/edit/', views.ExerciseUpdateView.as_view(), name='edit'),
    path('exercises/<pk>/delete/', views.ExerciseDeleteView.as_view(), name='delete'),
    path('exercises/copy/<pk>/', views.exercise_copy, name='copy'),

    # Exercise content
    path('exercises/<pk_exercise>/content/add/', views.ExerciseContentCreateView.as_view(), name='content-add'),
    path('exercises/<pk_exercise>/content/<pk>/edit/', views.ExerciseContentUpdateView.as_view(), name='content-edit'),
    path('exercises/<pk_exercise>/content/<pk>/delete/', views.ExerciseContentDeleteView.as_view(), name='content-delete')
]
