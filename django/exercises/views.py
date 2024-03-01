from django.views.generic import (View, DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView)
from django.db.models import Q
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from functools import reduce
from operator import (or_, and_)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from account.models import User
from . import models
from . import forms
from .exportdata.studentscores import exportstudentscores
import os


# UserExerciseAttempt


class UserExerciseAttemptView(View):
    """
    Class-based view to process the submission of the Student Exercise Attempt form
    From the detail page
    """
    def post(self, request, *args, **kwargs):
        # Build new object as dict
        attempt = {
            'exercise': models.Exercise.objects.get(id=self.request.POST.get('exercise', '')),
            'user': self.request.user
        }
        # Add score to attempt dict if it's provided
        score = self.request.POST.get('score', '')
        if score != '':
            attempt['score'] = score
        # Add attempt_detail to attempt dict if it's provided
        attempt_detail = self.request.POST.get('attempt_detail', '')
        if attempt_detail != '':
            attempt['attempt_detail'] = attempt_detail
        # Add attempt_duration to attempt dict if it's provided
        attempt_duration = self.request.POST.get('attempt_duration', '')
        if attempt_duration != '':
            attempt['attempt_duration'] = attempt_duration
        # Save object
        models.UserExerciseAttempt(**attempt).save()
        # Success redirect url
        return redirect('exercises:attempt-success')


class UserExerciseAttemptSuccessTemplateView(TemplateView):
    """
    Class-based view for user exercise attempt success template
    """
    template_name = 'exercises/exercise-attempt-success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the last attempt of this user (i.e. the one that has just been completed)
        context['last_attempt'] = models.UserExerciseAttempt.objects.filter(user=self.request.user).order_by('-submit_timestamp').first()
        return context


# Export Data: Student Scores


class ExportDataStudentScoresOptionsTemplateView(LoginRequiredMixin, TemplateView):
    """
    Class-based view for export data: student scores options template
    """
    template_name = 'exercises/exportdata-studentscores-options.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Return all classes if user is an admin
        if self.request.user.role.name == 'admin':
            context['classes'] = models.SchoolClass.objects.all()
        elif self.request.user.role.name == 'teacher':
            context['classes'] = models.SchoolClass.objects.filter(user__id=self.request.user.id)

        return context


@login_required
def exportdata_studentscores(request):
    """
    Creates an Excel spreadsheet containing student scores and return it to the user to download
    """

    # Only allow admins and teachers to export scores
    if request.user.role.name in ['admin', 'teacher']:
        file_path = exportstudentscores.create_workbook(request)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
                return response
    raise Http404


# Exercise


class ExerciseCreateView(PermissionRequiredMixin, CreateView):
    """
    Class-based view to show the exercise create template
    """

    template_name = 'exercises/exercise-add.html'
    model = models.Exercise
    fields = ['name', 'language', 'exercise_format', 'exercise_format_reverse_image_match', 'theme', 'difficulty', 'font_size', 'instructions', 'instructions_image', 'instructions_image_url', 'instructions_image_width_percent', 'is_a_formal_assessment', 'is_published']
    permission_required = ('exercises.add_exercise')
    success_url = reverse_lazy('exercises:list')

    def get_success_url(self):
        """
        Redirect to the current exercise that this createview is adding content to
        """
        return reverse_lazy('exercises:detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """
        Set the current user as the creator and owner
        """
        form.instance.created_by = self.request.user
        form.instance.owned_by = self.request.user
        return super().form_valid(form)


class ExerciseUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Class-based view to show the exercise update template
    """

    template_name = 'exercises/exercise-edit.html'
    model = models.Exercise
    fields = ['name', 'language', 'exercise_format_reverse_image_match', 'theme', 'difficulty', 'font_size', 'instructions', 'instructions_image', 'instructions_image_url', 'instructions_image_width_percent', 'is_a_formal_assessment', 'owned_by', 'collaborators', 'is_published']
    permission_required = ('exercises.change_exercise')

    def get_queryset(self):
        """
        Only show this page if the current user is an admin or a teacher who owns the exercise
        """
        q = super().get_queryset()
        return q if self.request.user.is_superuser else q.filter(Q(owned_by=self.request.user | Q(collaborators__in=[self.request.user])))

    def get_success_url(self, **kwargs):
        """
        Redirect to the current exercise that this createview is adding content to
        """
        return reverse_lazy('exercises:detail', kwargs={'pk': self.kwargs['pk']})


class ExerciseDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Class-based view for deleting exercises (including confirmation page)
    """

    template_name = 'exercises/exercise-confirmdelete.html'
    model = models.Exercise
    permission_required = ('exercises.delete_exercise')
    success_url = reverse_lazy('exercises:list')


def exercise_copy(request, pk):
    """
    This is a function view for allowing users to easy copy an existing exercise
    and its associated data (i.e. ExerciseFormat____ objects) and then redirecting
    the user to edit the newly generated exercise
    """
    # Get original exercise
    originalExercise = models.Exercise.objects.get(id=pk)
    # Make copy of exercise
    newExercise = originalExercise
    newExercise.name += ' (copy)'
    newExercise.created_by = request.user
    newExercise.owned_by = request.user
    newExercise.pk = None  # clear id so Django will provide a new, unique id automatically
    newExercise.save()

    # Find original ExerciseFormat_____ objects that link to the original Exercise
    originalParentExercise = models.Exercise.objects.get(id=pk)
    if originalParentExercise.exercise_format.name == 'Multiple Choice':
        originalFormatObjects = models.ExerciseFormatMultipleChoice.objects.filter(exercise=originalParentExercise)
    elif originalParentExercise.exercise_format.name == 'Fill in the Blank':
        originalFormatObjects = models.ExerciseFormatFillInTheBlank.objects.filter(exercise=originalParentExercise)
    elif originalParentExercise.exercise_format.name == 'Image Match':
        originalFormatObjects = models.ExerciseFormatImageMatch.objects.filter(exercise=originalParentExercise)
    elif originalParentExercise.exercise_format.name == 'Sentence Builder':
        originalFormatObjects = models.ExerciseFormatSentenceBuilder.objects.filter(exercise=originalParentExercise)
    elif originalParentExercise.exercise_format.name == 'Translation':
        originalFormatObjects = models.ExerciseFormatTranslation.objects.filter(exercise=originalParentExercise)
    elif originalParentExercise.exercise_format.name == 'External':
        originalFormatObjects = models.ExerciseFormatExternal.objects.filter(exercise=originalParentExercise)
    # Create new ExerciseFormat_____ objects that link to the new Exercise
    for originalFormatObject in originalFormatObjects:
        newFormatObject = originalFormatObject
        newFormatObject.pk = None
        newFormatObject.exercise = newExercise
        newFormatObject.save()
    # Take user to the new exercise
    return redirect(reverse_lazy('exercises:edit', kwargs={'pk': newExercise.id}))


class ExerciseDetailView(LoginRequiredMixin, DetailView):
    """
    Class-based view for exercise detail template
    """
    template_name = 'exercises/exercise-detail.html'
    model = models.Exercise

    def get_queryset(self):
        return self.model.objects.filter(Q(is_published=True) | Q(owned_by=self.request.user) | Q(collaborators__in=[self.request.user])).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If user is logged in, return past scores for current exercise
        if self.request.user.is_authenticated:
            context['pastscores'] = models.UserExerciseAttempt.objects.filter(exercise=self.object, user=self.request.user)
        return context


class ExerciseListView(LoginRequiredMixin, ListView):
    """
    Class-based view for exercise list template
    """
    template_name = 'exercises/exercise-list.html'
    model = models.Exercise
    paginate_by = 100

    def get_queryset(self):
        """
        This method returns a filtered and ordered query set by:
        1. Enforcing privacy rules (e.g. is_published)
        2. Searching
        3. Filtering
        4. Ordering
        5. Returning
        """

        # 1. Enforcing privacy rules

        # Only show published, unless user is owner or collaborator on exercise
        queryset = self.model.objects.filter(
            Q(is_published=True)
            |
            Q(owned_by=self.request.user)
            |
            Q(collaborators__in=[self.request.user])
        ).distinct()

        # Students can only see exercises if they're in that class
        if self.request.user.role.name == 'student':
            # Build list of filters: (language and difficulty)
            filters = []
            for school_class in self.request.user.classes.all():
                filters.append(
                    reduce(
                        and_,
                        (
                            Q(language=school_class.language),
                            Q(difficulty=school_class.difficulty)
                        )
                    )
                )
            # Apply filters to queryset (uses or_, as can be any)
            queryset = queryset.filter(reduce(or_, filters))

        # 2. Searching
        search = self.request.GET.get('search', '').strip()
        if search != '':
            queryset = queryset.filter(
                Q(id__contains=search) |
                Q(name__icontains=search) |
                Q(language__name__icontains=search) |
                Q(exercise_format__name__icontains=search) |
                Q(theme__name__icontains=search) |
                Q(difficulty__name__icontains=search)
            )

        # 3. Filtering
        # language
        language = self.request.GET.get('language', '')
        # if language is specified, filter on that language
        if language not in ['*', '']:
            queryset = queryset.filter(language=language)
        # format
        format = self.request.GET.get('format', '*')
        queryset = queryset.filter(exercise_format=format) if format != '*' else queryset
        # theme
        # works differently to others, as must return child and grandchild themes
        # which is found by finding theme name in child/grandchild theme name
        theme = self.request.GET.get('theme', '*')
        if theme != '*':
            theme_name = models.Theme.objects.get(id=theme).name
            queryset = queryset.filter(theme__name__contains=theme_name)
        # difficulty
        difficulty = self.request.GET.get('difficulty', '*')
        queryset = queryset.filter(difficulty=difficulty) if difficulty != '*' else queryset
        # myexercises
        myexercises = self.request.GET.get('myexercises', '*')
        if myexercises == 'todo':
            exercises_todo = User.objects.get(pk=self.request.user.id).exercises_todo
            queryset = queryset.filter(pk__in=exercises_todo)
        elif myexercises == 'completed':
            exercises_completed = User.objects.get(pk=self.request.user.id).exercises_completed
            queryset = queryset.filter(pk__in=exercises_completed)

        # 4. Ordering (aka 'organise' as also organises them into groups in the web interface)
        order = self.request.GET.get('organise', 'name')
        queryset = queryset.order_by(order)

        # 5. Returning
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Organise
        context['organise'] = self.request.GET.get('organise', 'name')
        # Add data for related models, e.g. for populating select lists, etc.
        if self.request.user.role.name == 'student':
            school_classes = models.SchoolClass.objects.filter(user__id=self.request.user.id)
            languages = models.Language.objects.filter(is_published=True, schoolclass__in=school_classes)
        else:
            languages = models.Language.objects.filter(is_published=True)
        context['languages'] = languages
        context['themes'] = models.Theme.objects.filter(is_published=True)
        context['formats'] = models.ExerciseFormat.objects.filter(is_published=True)
        context['difficulties'] = models.Difficulty.objects.all()

        return context


# Exercise Content (e.g. ExerciseFormat______ items)


class ExerciseContentCreateView(PermissionRequiredMixin, CreateView):
    """
    Class-based view to show the exercise content create template
    """

    template_name = 'exercises/exercise-content-add.html'
    permission_required = ('exercises.add_exercise')

    def get_form_class(self, **kwargs):
        """
        Return the correct form based on the current exercise's format (e.g. Multiple Choice)
        """
        # Get the current exercise id
        try:
            exercise = models.Exercise.objects.get(pk=self.kwargs['pk_exercise'])
        except self.model.DoesNotExist:
            raise Http404()
        # Only show if current user is admin or teacher who owns parent exercise
        if self.request.user.is_superuser or exercise.owned_by == self.request.user or self.request.user in exercise.collaborators:
            # Set the correct form
            if exercise.exercise_format.name == 'Multiple Choice':
                return forms.ExerciseFormatMultipleChoiceForm
            elif exercise.exercise_format.name == 'Fill in the Blank':
                return forms.ExerciseFormatFillInTheBlankForm
            elif exercise.exercise_format.name == 'Image Match':
                return forms.ExerciseFormatImageMatchForm
            elif exercise.exercise_format.name == 'Sentence Builder':
                return forms.ExerciseFormatSentenceBuilderForm
            elif exercise.exercise_format.name == 'Translation':
                return forms.ExerciseFormatTranslationForm
            elif exercise.exercise_format.name == 'External':
                return forms.ExerciseFormatExternalForm
        else:
            raise PermissionDenied()

    def get_queryset(self):
        """
        Only show this page if the current user is an admin or a teacher who owns the exercise
        """
        q = super().get_queryset()
        return q if self.request.user.is_superuser else q.filter(Q(owned_by=self.request.user | Q(collaborators__in=[self.request.user])))

    def form_valid(self, form, **kwargs):
        """
        Final processing before saving the form, if it's valid
        """
        # Set the exercise value
        try:
            form.instance.exercise = models.Exercise.objects.get(pk=self.kwargs['pk_exercise'])
        except self.model.DoesNotExist:
            raise Http404()
        # Save the item
        self.object = form.save(commit=False)
        self.object.save()
        # Return valid form
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        """
        Redirect to the current exercise that this createview is adding content to
        """
        return reverse_lazy('exercises:detail', kwargs={'pk': self.kwargs['pk_exercise']})


class ExerciseContentUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Class-based view to show the exercise content update template
    """

    template_name = 'exercises/exercise-content-edit.html'
    permission_required = ('exercises.change_exercise')

    def get_queryset(self, **kwargs):
        """
        Determine the correct queryset (model) based on the current exercise's format
        """
        # Get the current exercise id
        try:
            exercise = models.Exercise.objects.get(pk=self.kwargs['pk_exercise'])
        except self.model.DoesNotExist:
            raise Http404()
        # Set the correct queryset
        if exercise.exercise_format.name == 'Multiple Choice':
            return models.ExerciseFormatMultipleChoice.objects.all()
        elif exercise.exercise_format.name == 'Fill in the Blank':
            return models.ExerciseFormatFillInTheBlank.objects.all()
        elif exercise.exercise_format.name == 'Image Match':
            return models.ExerciseFormatImageMatch.objects.all()
        elif exercise.exercise_format.name == 'Sentence Builder':
            return models.ExerciseFormatSentenceBuilder.objects.all()
        elif exercise.exercise_format.name == 'Translation':
            return models.ExerciseFormatTranslation.objects.all()
        elif exercise.exercise_format.name == 'External':
            return models.ExerciseFormatExternal.objects.all()

    def get_form_class(self, **kwargs):
        """
        Return the correct form based on the current exercise's format (e.g. Multiple Choice)
        """
        # Get the current exercise id
        try:
            exercise = models.Exercise.objects.get(pk=self.kwargs['pk_exercise'])
        except self.model.DoesNotExist:
            raise Http404()
        # Set the correct form
        if exercise.exercise_format.name == 'Multiple Choice':
            return forms.ExerciseFormatMultipleChoiceForm
        elif exercise.exercise_format.name == 'Fill in the Blank':
            return forms.ExerciseFormatFillInTheBlankForm
        elif exercise.exercise_format.name == 'Image Match':
            return forms.ExerciseFormatImageMatchForm
        elif exercise.exercise_format.name == 'Sentence Builder':
            return forms.ExerciseFormatSentenceBuilderForm
        elif exercise.exercise_format.name == 'Translation':
            return forms.ExerciseFormatTranslationForm
        elif exercise.exercise_format.name == 'External':
            return forms.ExerciseFormatExternalForm

    def form_valid(self, form, **kwargs):
        """
        Final processing before saving the form, if it's valid
        """
        # Set the exercise value
        try:
            form.instance.exercise = models.Exercise.objects.get(pk=self.kwargs['pk_exercise'])
        except self.model.DoesNotExist:
            raise Http404()
        # Save the item
        self.object = form.save(commit=False)
        self.object.save()
        # Return valid form
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        """
        Redirect to the current exercise that this createview is adding content to
        """
        return reverse_lazy('exercises:detail', kwargs={'pk': self.kwargs['pk_exercise']})


class ExerciseContentDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Class-based view for deleting exercise content item (including confirmation page)
    """

    template_name = 'exercises/exercise-content-confirmdelete.html'
    permission_required = ('exercises.delete_exercise')

    def get_queryset(self, **kwargs):
        """
        Determine the correct queryset (model) based on the current exercise's format
        """
        # Get the current exercise id
        try:
            exercise = models.Exercise.objects.get(pk=self.kwargs['pk_exercise'])
        except self.model.DoesNotExist:
            raise Http404()
        # Set the correct queryset
        if exercise.exercise_format.name == 'Multiple Choice':
            return models.ExerciseFormatMultipleChoice.objects.all()
        elif exercise.exercise_format.name == 'Fill in the Blank':
            return models.ExerciseFormatFillInTheBlank.objects.all()
        elif exercise.exercise_format.name == 'Image Match':
            return models.ExerciseFormatImageMatch.objects.all()
        elif exercise.exercise_format.name == 'Sentence Builder':
            return models.ExerciseFormatSentenceBuilder.objects.all()
        elif exercise.exercise_format.name == 'Translation':
            return models.ExerciseFormatTranslation.objects.all()
        elif exercise.exercise_format.name == 'External':
            return models.ExerciseFormatExternal.objects.all()

    def get_success_url(self, **kwargs):
        """
        Redirect to the current exercise that this createview is adding content to
        """
        return reverse_lazy('exercises:detail', kwargs={'pk': self.kwargs['pk_exercise']})
