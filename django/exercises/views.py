from django.views.generic import (View, DetailView, ListView, CreateView, UpdateView, DeleteView, TemplateView)
from django.db.models import Q
from django.db import models as django_models
from django.contrib.auth.mixins import (LoginRequiredMixin, PermissionRequiredMixin)
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from functools import reduce
from operator import (or_, and_)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from account.models import User
from . import models
from . import forms
from .exportdata.studentscores import export_studentscores_excel
import os


# Reusable code


def custom_permission_exercise_edit(user, exercise_obj):
    """
    Allow a specific/custom permission for editing exercises
    Exercises can be edited if the user is:
    - An admin
    - The owner of the exercise
    - A collaborator

    Return True if at least one of these conditions is met, else return false
    """

    return \
        user.is_superuser \
        or exercise_obj.owned_by == user \
        or user in exercise_obj.collaborators.all()


def api_authentication(request):
    """
    Complete authentication checks for API (data export/import) views
    Returns a tuple of: (True/False, message)
    """

    username = request.GET.get('username')
    api_key = request.GET.get('api_key')
    if not (username and api_key):
        return (False, 'Authentication parameters not provided: username, api_key')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return (False, 'Authentication failed: no user found with this username')
    if not user.api_authentication(api_key):
        return (False, 'Authentication failed: no user found with matching username and api_key')
    # Passes authentication check
    return (True, 'Authentication success')


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


# Exercise


class ExerciseCreateView(PermissionRequiredMixin, CreateView):
    """
    Class-based view to show the exercise create template
    """

    template_name = 'exercises/exercise-add.html'
    model = models.Exercise
    fields = ['name', 'language', 'exercise_format', 'exercise_format_reverse_image_match', 'theme', 'difficulty', 'font_size', 'instructions', 'instructions_image', 'instructions_image_url', 'instructions_image_width_percent', 'instructions_video_url', 'is_a_formal_assessment', 'is_published']
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
    fields = [
        'name', 'language', 'exercise_format_reverse_image_match', 'theme', 'difficulty',
        'font_size', 'instructions', 'instructions_image', 'instructions_image_url',
        'instructions_image_width_percent', 'instructions_video_url', 'is_a_formal_assessment',
        'owned_by', 'collaborators', 'is_published'
    ]
    permission_required = ('exercises.change_exercise')

    def get_object(self):
        """
        Only show this page if the current user passes custom permission check
        """
        exercise = super().get_object()
        if custom_permission_exercise_edit(self.request.user, exercise):
            return exercise
        else:
            raise PermissionDenied()

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
        context['custom_permission_exercise_edit'] = custom_permission_exercise_edit(self.request.user, self.object)
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
        if custom_permission_exercise_edit(self.request.user, exercise):
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
        # Only show if current user is admin or teacher who owns parent exercise
        if custom_permission_exercise_edit(self.request.user, exercise):
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
        else:
            raise PermissionDenied()

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


# Export Data: Excel


class ExportDataExcelStudentScoresOptionsTemplateView(LoginRequiredMixin, TemplateView):
    """
    Class-based view for export data: student scores options template
    """
    template_name = 'exercises/exportdata-excel-studentscores-options.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Return all classes if user is an admin
        if self.request.user.role.name == 'admin':
            context['classes'] = models.SchoolClass.objects.all()
        elif self.request.user.role.name == 'teacher':
            context['classes'] = models.SchoolClass.objects.filter(user__id=self.request.user.id)

        return context


@login_required
def exportdata_excel_studentscores(request):
    """
    Creates an Excel spreadsheet containing student scores and return it to the user to download
    """

    # Only allow admins and teachers to export scores
    if request.user.role.name in ['admin', 'teacher']:
        file_path = export_studentscores_excel.create_workbook(request)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
                response['Content-Disposition'] = f'inline; filename={os.path.basename(file_path)}'
                return response
    raise Http404


# Export Data: JSON


class ExportDataJsonTemplateView(LoginRequiredMixin, TemplateView):
    """
    Class-based view for export data (JSON) information template
    """
    template_name = 'exercises/exportdata-json.html'


def exportdata_json_studentscores(request):
    """
    Returns JSON data containing UserExerciseAttempt objects and related data
    Requires 'username' and 'api_key' in GET query parameters
    """

    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)

    # User Authentication
    authentication_success, authentication_msg = api_authentication(request)
    if not authentication_success:
        return JsonResponse({'error': authentication_msg}, status=400)

    studentscores = models.UserExerciseAttempt.objects.filter(user__role__name='student')\
        .select_related(
        'exercise',
        'exercise__language',
        'exercise__exercise_format',
        'exercise__theme',
        'exercise__difficulty',
        'user'
    )
    studentscores_list = []

    for studentscore in studentscores:
        studentscores_list.append({
            'exercise_id': studentscore.exercise.id,
            'exercise_url': request.build_absolute_uri(f'/exercises/{studentscore.exercise.id}'),
            'exercise_language': str(studentscore.exercise.language),
            'exercise_format': str(studentscore.exercise.exercise_format),
            'exercise_theme': str(studentscore.exercise.theme),
            'exercise_difficulty': str(studentscore.exercise.difficulty),
            'user_id': studentscore.user.id,
            'user_username': studentscore.user.username,
            'user_internal_id': studentscore.user.internal_id_number,
            'attempt_id': studentscore.id,
            'attempt_score': studentscore.score,
            'attempt_detail': studentscore.attempt_detail,
            'attempt_duration': studentscore.attempt_duration,
            'attempt_submit_timestamp': studentscore.submit_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse(studentscores_list, safe=False)


def exportdata_json_exercises(request):
    """
    Returns JSON data containing Exercise objects and related data
    Requires 'username' and 'api_key' in GET query parameters
    """

    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)

    # User Authentication
    authentication_success, authentication_msg = api_authentication(request)
    if not authentication_success:
        return JsonResponse({'error': authentication_msg}, status=400)

    # Define the Exercise data to include
    exercises = models.Exercise.objects.all().select_related(
        'exercise_format',
        'language',
        'theme',
        'difficulty',
        'owned_by',
        'created_by'
    ).order_by('id')
    exercises_list = []

    # Loop through the objects and build a dictionary for each
    for exercise in exercises:
        # Build exercise items data for current Exercise object
        exercise_items_model = None
        exercise_items_data = None
        # Determine the model
        exercise_format = exercise.exercise_format.name.lower()
        if exercise_format == 'image match':
            exercise_items_model = models.ExerciseFormatImageMatch
        elif exercise_format == 'multiple choice':
            exercise_items_model = models.ExerciseFormatMultipleChoice
        elif exercise_format == 'fill in the blank':
            exercise_items_model = models.ExerciseFormatFillInTheBlank
        elif exercise_format == 'sentence builder':
            exercise_items_model = models.ExerciseFormatSentenceBuilder
        elif exercise_format == 'translation':
            exercise_items_model = models.ExerciseFormatTranslation
        elif exercise_format == 'external':
            exercise_items_model = models.ExerciseFormatExternal

        # Get all data for objects of the chosen model that belong to this Exercise
        if exercise_items_model:
            exercise_items_data = list(exercise_items_model.objects.filter(exercise=exercise).values())

        # Add this Exercise to the list of exercises
        exercises_list.append({
            'id': exercise.id,
            'name': exercise.name,
            'language': str(exercise.language),
            'exercise_format': str(exercise.exercise_format),
            'exercise_format_reverse_image_match': exercise.exercise_format_reverse_image_match,
            'theme': str(exercise.theme),
            'difficulty': str(exercise.difficulty),
            'font_size': exercise.font_size,
            'instructions': exercise.instructions,
            'instructions_image': exercise.instructions_image.url if exercise.instructions_image else None,
            'instructions_image_url': exercise.instructions_image_url,
            'instructions_image_width_percent': exercise.instructions_image_width_percent,
            'instructions_video_url': exercise.instructions_video_url,
            'is_a_formal_assessment': exercise.is_a_formal_assessment,
            'is_published': exercise.is_published,
            'owned_by': str(exercise.owned_by),
            'created_by': str(exercise.created_by),
            'created_datetime': exercise.created_datetime,
            'lastupdated_datetime': exercise.lastupdated_datetime,

            # Exercise items data
            'exercise_items': exercise_items_data
        })

    return JsonResponse(exercises_list, safe=False)


def exportdata_json_generic(request, model, fields):
    """
    This is a simple, generic function that can be used to export JSON data
    for most models, where each model will require separate functional view calling this
    e.g. return exportdata_json_generic(request, models.Difficulty, ['id', 'name'])

    Returns JSON data for specified model (or error message)

    Requires 'username' and 'api_key' in GET query parameters
    """

    if request.method != 'GET':
        return JsonResponse({'error': 'GET required'}, status=405)

    # User Authentication
    authentication_success, authentication_msg = api_authentication(request)
    if not authentication_success:
        return JsonResponse({'error': authentication_msg}, status=400)

    # Define the Exercise data to include
    data_queryset = model.objects.all()
    data_list = []

    for data_object in data_queryset:
        data_item = {}
        for field in fields:
            field_type = type(model._meta.get_field(field))
            field_value = getattr(data_object, field)
            # Force FK fields where value isn't None to be strings, so can be processed as JSON
            if field_value and field_type == django_models.fields.related.ForeignKey:
                field_value = str(field_value)
            # Add field value to the data item
            data_item[field] = field_value
        data_list.append(data_item)

    return JsonResponse(data_list, safe=False)


def exportdata_json_yeargroups(request):
    """
    Return JSON data of all YearGroup objects
    """

    model = models.YearGroup
    fields = ['id', 'name', 'date_start', 'date_end', 'is_published']
    return exportdata_json_generic(request, model, fields)


def exportdata_json_difficulties(request):
    """
    Return JSON data of all Difficulty objects
    """

    model = models.Difficulty
    fields = ['id', 'name', 'order']
    return exportdata_json_generic(request, model, fields)


def exportdata_json_languages(request):
    """
    Return JSON data of all Language objects
    """

    model = models.Language
    fields = ['id', 'name', 'is_published']
    return exportdata_json_generic(request, model, fields)


def exportdata_json_fontsizes(request):
    """
    Return JSON data of all FontSize objects
    """

    model = models.FontSize
    fields = ['id', 'name', 'size_em']
    return exportdata_json_generic(request, model, fields)


def exportdata_json_schoolclasses(request):
    """
    Return JSON data of all SchoolClass objects
    """

    model = models.SchoolClass
    fields = [
        'id',
        'year_group',
        'language',
        'difficulty',
        'unique_feature',
        'is_published',
        'is_active'
    ]
    return exportdata_json_generic(request, model, fields)


def exportdata_json_themes(request):
    """
    Return JSON data of all Theme objects
    """

    model = models.Theme
    fields = ['id', 'name', 'is_published']
    return exportdata_json_generic(request, model, fields)


def exportdata_json_exerciseformats(request):
    """
    Return JSON data of all ExerciseFormat objects
    """

    model = models.ExerciseFormat
    fields = [
        'id',
        'name',
        'icon',
        'instructions',
        'is_marked_automatically_by_system',
        'is_published'
    ]
    return exportdata_json_generic(request, model, fields)
