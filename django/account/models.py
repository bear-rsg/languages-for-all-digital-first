from django.contrib.auth.models import AbstractUser, Group
from django.apps import apps
from django.db import models


class UserRole(models.Model):
    """
    Role for each user, e.g. Student, Teacher, Admin
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom user extends the standard Django user model, providing additional properties
    """

    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, blank=True, null=True)
    classes = models.ManyToManyField('exercises.SchoolClass', blank=True)
    default_language = models.ForeignKey('exercises.Language', on_delete=models.SET_NULL, blank=True, null=True)

    @property
    def name(self):
        """
        Return the full name (e.g. first and last names, if not null)
        If no first or last name, returns username
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name and not self.last_name:
            return self.first_name
        elif not self.first_name and self.last_name:
            return self.last_name
        else:
            return self.username

    @property
    def exercises_completed(self):
        """
        Build and return a list of id's of Exercise objects
        The exercises exist for this user in UserExerciseAttempt
        """
        return [a.exercise.id for a in self.userexerciseattempt_set.all()]

    @property
    def exercises_todo(self):
        """
        Build and return a list of id's of Exercise objects
        The exercises are marked as 'active' in SchoolClassAlertExercise for classes this user belongs to
        and have also not already been completed
        To get these exercises, this goes through 2 m2m relationships (user <> class <> classalert)
        """
        exercises = []
        for c in self.classes.all():
            for a in apps.get_model('exercises.SchoolClassAlertExercise').objects.filter(school_class=c):
                # Confirm the alert is active and that the user hasn't already completed the exercise
                if a.is_active and a.exercise.id not in self.exercises_completed:
                    exercises.append(a.exercise.id)
        return exercises

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Username to be same as email
        self.username = self.email
        # Set values for admins
        if self.role == UserRole.objects.get(name='admin'):
            self.is_staff = True
            self.is_superuser = True
        # Set values for teachers
        if self.role == UserRole.objects.get(name='teacher'):
            self.is_staff = True
            self.is_superuser = False
        # Set values for students
        if self.role == UserRole.objects.get(name='student'):
            self.is_staff = False
            self.is_superuser = False
        # Save object
        super().save(*args, **kwargs)

        # Once user is saved, add to necessary permission group
        # teacher_permissions_group
        if self.role == UserRole.objects.get(name='teacher'):
            Group.objects.get(name='teacher_permissions_group').user_set.add(self)
