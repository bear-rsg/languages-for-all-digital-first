from django.contrib.auth.models import AbstractUser, Group
from django.apps import apps
from django.db import models
import os


class UserRole(models.Model):
    """
    Role for each user, e.g. Student, Teacher, Admin, Guest
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class UsersImportSpreadsheet(models.Model):
    """
    An Excel spreadsheet containing new user data to import into the database
    """

    spreadsheet = models.FileField(upload_to='account/userimportspreadsheets',
                                   help_text="""Upload an Excel spreadsheet (.xlsx) with data of new users to add to the database.<br>\
Ensure the structure complies with the latest version of the template spreadsheet or the import may fail.<br>\
Contact the software developer for support if you require help.<br>\
Once you've uploaded the file, you can begin <a href="/account/importdata/">the import process</a>""",
                                   blank=True,
                                   null=True)
    lastupdated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    @property
    def spreadsheet_filename(self):
        return str(os.path.basename(self.spreadsheet.name))

    def __str__(self):
        return self.spreadsheet_filename


class User(AbstractUser):
    """
    Custom user extends the standard Django user model, providing additional properties
    """

    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, blank=True, null=True)
    is_internal = models.BooleanField(default=True, help_text='Is internal to the University of Birmingham, e.g. an active UoB student or staff member')
    internal_id_number = models.CharField(max_length=255, help_text='If internal to the University of Birmingham, please provide a unique ID, e.g. student number, staff number', blank=True)
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
        # Set as admin if user hasn't been given a role (e.g. created using 'createsuperuser')

        # Set default role of student if one isn't provided at account creation
        if not self.role:
            self.role = UserRole.objects.get(name='student')
            # If user is created using 'createsuperuser' upgrade them to admin
            if self.is_superuser:
                self.role = UserRole.objects.get(name='admin')

        # Set values for admins
        if self.role.name == 'admin':
            self.is_staff = True
            self.is_superuser = True
        # Set values for teachers and guests
        elif self.role.name in ['teacher', 'guest']:
            self.is_staff = True
            self.is_superuser = False
        # Set values for students
        elif self.role.name == 'student':
            self.is_staff = False
            self.is_superuser = False
        # Save object
        super().save(*args, **kwargs)

        # Once user is saved, add to necessary permission group
        self.groups.clear()
        if self.role.name == 'teacher':
            Group.objects.get(name='teacher_permissions_group').user_set.add(self)
        elif self.role.name == 'guest':
            Group.objects.get(name='guest_permissions_group').user_set.add(self)
