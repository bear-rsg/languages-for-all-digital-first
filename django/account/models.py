from django.contrib.auth.models import AbstractUser
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
